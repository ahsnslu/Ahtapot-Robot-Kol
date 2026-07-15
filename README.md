🐙 Biyomimetik Ahtapot (Continuum) Robot Kol Tasarımı, Kinematik Analizi ve Simülasyonu
Bu proje; doğadaki ahtapot kollarının eklemsiz, tamamen esnek ve uç kısma doğru daralan (tapered)
morfolojisinden esinlenerek geliştirilen Sürekli Esnek (Continuum) Robot Kol sisteminin mekanik tasarımını, 
kinematik denklemlerini ve simülasyon algoritmalarını içermektedir.

⚠️ Önemli Not: Bu çalışma, Türkiye'de akademik veya endüstriyel düzeyde daha önce benzeri gerçekleştirilmemiş öncü bir Continuum Robotik projesidir.
Dünya genelinde ise yalnızca MIT, Harvard ve Stanford gibi lider kurumların ileri düzey robotik laboratuvarlarında araştırılan bu karmaşık sistemi;
mekanik tasarımdanmatematiksel modellemeye ve yazılıma kadar tüm disiplinleriyle tek başıma çalışarak hayata geçirdim.
<img width="1000" height="817" alt="SS" src="https://github.com/user-attachments/assets/f3469ff6-2038-45e6-93c1-a0e1c9443bba" />



📌 Projenin Öne Çıkan Özellikleri & Teknik Özgünlük
Öncü Biyomimetik Yaklaşım: Rijit (geleneksel eklemli) robot kollarının aksine, sıfır rijit eklem ile sürekli bükülme kabiliyetine sahip esnek omurga mimarisi.

Tüm Disiplinlerin Tek Elden Yönetimi: Mekanik CAD tasarımı (SolidWorks), ileri seviye kinematik matematiksel modellemeler ve simülasyon yazılımlarının tamamı tek bir mühendis tarafından geliştirilmiştir.

Gelişmiş Çift Kinematik Modelleme:
Sabit Eğrilik (Constant Curvature)Simülasyonu (continuum_robot_sim.py): Doğrusal daralan kesit yarıçapı ile çoklu yükleme senaryolarınıanaliz eder ve anlık bükülmeaçılarını hesaplar.

Logaritmik Spiral (Spiro) Simülasyonu (spiro_robot_sim.py):Boyutları ve segment uzunlukları geometrik bir oranla sönümlenen (decay_ratio), kendi üzerine tam turlarla katlanabilen sarmal manipülatör modelidir.

📐 Kinematik Modeller ve Matematiksel AltyapıSürekli esnek (continuum) robotlar, klasik D-H parametreleri ve kartezyen eklem matrisleri ile modellenemezler. Bu projede kullanılan matematiksel çözümler:
1. Sabit Eğrilikli Kinematik Model (Constant-Curvature Model)Esnek gövde, N adet sonlu alt segmente bölünür. Toplam bükülme açısı theta, her segmente homojen dağıtılarak lokal eğrilik açısı Delta theta elde edilir:


   <img width="231" height="117" alt="image" src="https://github.com/user-attachments/assets/55985094-38b0-4fcb-bb44-766ee1832b91" />

Her segmentin yönelimi (heading angle) birikimli olarak hesaplanır:

                                            
   <img width="252" height="132" alt="image" src="https://github.com/user-attachments/assets/d824e2f1-8b2e-4d85-8fde-2ad51c5fde32" />
                                        
Segmentlerin dış yarıçapı R_i, tabandan Rbase uca doğru lineer olarak daralarak gerçekçi bir konik form oluşturur:

   <img width="532" height="150" alt="image" src="https://github.com/user-attachments/assets/75ec335a-db99-4ea0-9b4b-b3f4d60cae53" />


2. Logaritmik Spiral Model (Logarithmic-Spiral Continuum)Doğal ahtapot kollarının sarmal büzülme mekanizması, segment uzunluklarının (L_i) ve çaplarının (D_i) sabit bir geometrik sönüm çarpanı (r < 1) ile küçülmesi esasına dayanır:
  <img width="247" height="207" alt="image" src="https://github.com/user-attachments/assets/d3706c68-2226-467f-9e40-c7ca74bba3fb" />


🛠 SolidWorks 3D CAD Mekanik Tasarımı
Projenin fiziksel prototip altyapısını oluşturan SolidWorks montaj dosyaları şu temel mekanik unsurları içerir:

Segmentli Esnek Omurga (Vertebrae): Robotun bükülme esnasında aşırı burulmasını (torsiyon) engelleyen, esneklik limiti yüksek, birbirine geçmeli kanal diskleri.

Tendon Kılavuz Kanalları: Disklerin çevrelerine 120 açılarla yerleştirilen kılavuz delikler, tahrik motorlarından gelen çelik tellerin (tendonların) minimum sürtünmeyle geçmesini sağlar.

Konik Daralan Geometri: Gövdenin uca doğru incelmesi, uç efektörün hassas kontrolünü sağlarken tabandaki motorların statik yükünü hafifletir.

💻 Yazılım ve Simülasyon Setup
Simülasyon kodları, robotun esnek yapısını ve bükülme davranışlarını görselleştirmek için Python dilinde matplotlib ve numpy kütüphaneleri kullanılarak optimize edilmiştir.

🔌 Gereksinimler
Gerekli kütüphaneleri hızlıca kurmak için terminalinizde çalıştırın:
pip install -r requirements.txt

🚀Simülasyonları Çalıştırma
1. Sabit Eğrilikli Continuum Simülasyonu
Farklı bükülme açılarındaki robot konfigürasyonlarını ve mühendislik eğrilik grafiklerini analiz etmek için:

python continuum_robot_sim.py --angles 30 90 160 --segments 40

2. Logaritmik Spiral Simülasyonu
Robotun kendi üzerine sarılan konik sarmal yapısını test etmek için:

python spiro_robot_sim.py --angle 540 --segments 35 --ratio 0.93

👥 Geliştirici & Araştırmacı
Ahsen Uslu - Mekatronik Mühendisliği, Erciyes Üniversitesi


<img width="1075" height="587" alt="image" src="https://github.com/user-attachments/assets/7c1fcfab-28d8-4b08-b279-392a0993c069" />




