import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk

#Malzeme seçenekleri
malzemeler = {
    "Alüminyum": 0.02,
    "Kurşun": 0.1,
    "Çelik": 0.05,
    "Bakır": 0.03,
    "Demir": 0.04,
    "Altın": 0.12,
    "Tungsten": 0.15
}

#Radyoaktif kaynak seçenekleri 
kaynaklar = {
    "Co-60": {"I0": 100, "enerji": 1.17},
    "Cs-137": {"I0": 80, "enerji": 0.66},
    "Na-22": {"I0": 120, "enerji": 0.511}
}


def start_simulation():
    global mu, malzeme_kalinlik, secili_kaynaklar
    malzeme_secim = malzeme_var.get()
    malzeme_kalinlik = float(kalinlik_var.get())
    mu = malzemeler[malzeme_secim]
    
    # Seçili kaynaklar
    secili_kaynaklar = []
    for var, key in zip(kaynak_vars, kaynaklar.keys()):
        if var.get():
            secili_kaynaklar.append((key, kaynaklar[key]))
    
    if not secili_kaynaklar:
        # Hiç kaynak seçilmezse default olarak ilk kaynak
        secili_kaynaklar.append((list(kaynaklar.keys())[0], list(kaynaklar.values())[0]))
    
    root.destroy()

root = tk.Tk()
root.title("Gama Simülasyonu Seçimleri")

tk.Label(root, text="Malzeme Seçin:").grid(row=0, column=0, padx=10, pady=5)
malzeme_var = tk.StringVar(value=list(malzemeler.keys())[0])
ttk.Combobox(root, textvariable=malzeme_var, values=list(malzemeler.keys())).grid(row=0, column=1)

tk.Label(root, text="Radyoaktif Kaynak Seçin:").grid(row=1, column=0, padx=10, pady=5)
kaynak_vars = []
for i, key in enumerate(kaynaklar.keys()):
    var = tk.BooleanVar(value=False)
    chk = tk.Checkbutton(root, text=key, variable=var)
    chk.grid(row=1+i, column=1, sticky='w')
    kaynak_vars.append(var)

tk.Label(root, text="Malzeme Kalınlığı (mm):").grid(row=5, column=0, padx=10, pady=5)
kalinlik_var = tk.StringVar(value="30")
tk.Entry(root, textvariable=kalinlik_var).grid(row=5, column=1)

tk.Button(root, text="Simülasyonu Başlat", command=start_simulation).grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()


fotons_list = []
renkler_list = []
for idx, (kaynak_adi, kaynak) in enumerate(secili_kaynaklar):
    I0 = kaynak["I0"]
    enerji = kaynak["enerji"]
    fotons = np.zeros((I0, 3))  # x, y, enerji
    fotons[:,1] = np.linspace(0, 10, I0)
    fotons[:,2] = np.full(I0, enerji)
    fotons_list.append(fotons)
    renkler_list.append(plt.cm.tab10(idx % 10))


fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(18,5))

# 2D simülasyon plot
all_fotons = np.vstack(fotons_list)
all_colors = np.concatenate([np.full(f.shape[0], i) for i, f in enumerate(fotons_list)])
scat = ax1.scatter(all_fotons[:,0], all_fotons[:,1], c=[renkler_list[int(c)] for c in all_colors])
ax1.set_xlim(0, 60)
ax1.set_ylim(0, 10)
ax1.set_title("2D Gama Simülasyonu")
ax1.set_xlabel("X pozisyonu (mm)")
ax1.set_ylabel("Y pozisyonu (mm)")

# Detektöre ulaşan foton sayısı
x_graf = [0]
y_graf = [all_fotons.shape[0]]
line, = ax2.plot(x_graf, y_graf, marker='o', label="Detektöre Ulaşan Foton")
ax2.set_xlim(0, 60)
ax2.set_ylim(0, all_fotons.shape[0]+10)
ax2.set_title("Detektöre Ulaşan Foton Sayısı")
ax2.set_xlabel("X pozisyonu (mm)")
ax2.set_ylabel("Foton Sayısı")
ax2.grid(True)
ax2.legend()

# Enerji histogramı
hist_bins = np.linspace(0, max(all_fotons[:,2])*1.2, 20)
ax3.hist(all_fotons[:,2], bins=hist_bins, color='orange', alpha=0.7)
ax3.set_xlim(0, max(all_fotons[:,2])*1.2)
ax3.set_ylim(0, all_fotons.shape[0]/2)
ax3.set_title("Enerji Spektrumu")
ax3.set_xlabel("Enerji (MeV)")
ax3.set_ylabel("Foton Sayısı")
ax3.grid(True)


def update(frame):
    global fotons_list, all_fotons
    
    for fotons in fotons_list:
        fotons[:,0] += 1
        absorbe = (fotons[:,0] >= malzeme_kalinlik) & (np.random.rand(fotons.shape[0]) < mu)
        fotons[absorbe,0] = -1
    
    # Tüm fotonları birleştir
    all_fotons = np.vstack(fotons_list)
    
    # 2D animasyon
    all_colors = np.concatenate([np.full(f.shape[0], i) for i, f in enumerate(fotons_list)])
    scat.set_offsets(all_fotons[:,:2])
    scat.set_color([renkler_list[int(c)] for c in all_colors])
    
    # Detektöre ulaşan foton sayısı
    x_graf.append(frame)
    y_graf.append(np.sum(all_fotons[:,0] >= 50))
    line.set_data(x_graf, y_graf)
    
    # Enerji histogramı
    ax3.cla()
    ax3.hist(all_fotons[all_fotons[:,0]>=50,2], bins=hist_bins, color='orange', alpha=0.7)
    ax3.set_xlim(0, max(all_fotons[:,2])*1.2)
    ax3.set_ylim(0, all_fotons.shape[0]/2)
    ax3.set_title("Enerji Spektrumu")
    ax3.set_xlabel("Enerji (MeV)")
    ax3.set_ylabel("Foton Sayısı")
    ax3.grid(True)
    
    return scat, line

ani = animation.FuncAnimation(fig, update, frames=60, interval=100, blit=False)
plt.tight_layout()
plt.show()
