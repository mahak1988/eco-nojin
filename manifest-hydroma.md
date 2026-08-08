# 📜 برنامه جامع توسعه علمی پلتفرم هیدروما نوژین
## چارچوب چند-رشته‌ای، چند-مقیاسی و دانش‌بنیان

---

## بخش اول: منظومه ماهواره‌ای و فیزیک سنجش از دور

### ۱.۱. معماری منظومه ماهواره‌ای (Satellite Constellation Architecture)

پلتفرم هیدروما نوژین از یک منظومه ۱۱ ماهواره‌ای رایگان استفاده می‌کند که هر لایه از سیستم زمینی را پوشش می‌دهد:

#### لایه اول: رادار فعال (Active Microwave)

| ماهواره | سنسور | باند | رزولوشن | دوره بازگشت | کاربرد اصلی |
|---------|--------|------|---------|-------------|-------------|
| Sentinel-1A/B | C-SAR | C-Band (5.6 cm) | 5×20 m | 6 روز | رطوبت خاک، فرونشست، بیوماس |
| Sentinel-6 | Poseidon-4 | Ku-Band | 300 m | 10 روز | ارتفاع‌سنجی دقیق سطح آب |
| GPM Core | DPR | Ku/Ka-Band | 5 km | 3 ساعت | بارش سه‌بعدی جهانی |

**فیزیک حاکم بر رادار C-Band:**

معادله رادار (Radar Equation):

$$P_r = \frac{P_t G^2 \lambda^2 \sigma^0 A_r}{(4\pi)^3 R^4}$$

که در آن:
- $P_t$: توان ارسالی
- $G$: بهره آنتن
- $\lambda$: طول موج (5.6 cm برای C-Band)
- $\sigma^0$: سطح مقطع پس‌پراکندگی نرمال‌شده
- $R$: فاصله تا هدف

#### لایه دوم: اپتیکال/حرارتی (Optical/Thermal)

| ماهواره | سنسور | باندها | رزولوشن | دوره بازگشت | کاربرد اصلی |
|---------|--------|--------|---------|-------------|-------------|
| Sentinel-2A/B | MSI | 13 باند VIS-NIR-SWIR | 10-60 m | 5 روز | فنولوژی، کلروفیل، آب برگ |
| Sentinel-3A/B | SLSTR | 9 باند | 300 m-1 km | روزانه | دمای سطح، تبخیر-تعرق |
| Landsat 8/9 | OLI/TIRS | 11 باند | 15-100 m | 16 روز | تاریخچه 40 ساله، ET |
| VIIRS (Suomi NPP) | VIIRS | 22 باند | 375 m | روزانه | آتش‌سوزی، فنولوژی |

**فیزیک انتقال تابش در جو:**

معادله انتقال تابش (Radiative Transfer Equation):

$$L_\lambda(\tau) = L_\lambda(0) e^{-\tau} + \int_0^\tau B_\lambda(T(\tau')) e^{-(\tau-\tau')} d\tau'$$

که در آن:
- $L_\lambda$: شدت تابش در طول موج $\lambda$
- $\tau$: عمق اپتیکی جو
- $B_\lambda(T)$: تابش جسم سیاه (قانون پلانک):

$$B_\lambda(T) = \frac{2hc^2}{\lambda^5} \cdot \frac{1}{e^{hc/\lambda k_B T} - 1}$$

#### لایه سوم: جوّی و شیمیایی (Atmospheric/Chemical)

| ماهواره | سنسور | گازهای هدف | رزولوشن | کاربرد |
|---------|--------|------------|---------|--------|
| Sentinel-5P | TROPOMI | NO₂, CH₄, CO, HCHO, O₃ | 7×3.5 km² | پایش آلودگی، کود |
| Aura | OMI | NO₂, SO₂, HCHO | 13×24 km | تاریخچه 20 ساله |
| GOSAT-2 | TANSO-FTS | CO₂, CH₄ | 2.5 km | گازهای گلخانه‌ای |

**الگوریتم DOAS (Differential Optical Absorption Spectroscopy):**

$$\ln\left[\frac{I_0(\lambda)}{I(\lambda)}\right] = \sum_i \sigma_i(\lambda) \cdot SCD_i + \sum_k a_k \lambda^k + \epsilon(\lambda)$$

که:
- $I_0$: شدت مرجع (بدون جذب)
- $I$: شدت اندازه‌گیری‌شده
- $\sigma_i$: سطح مقطع جذب گاز $i$
- $SCD_i$: چگالی ستونی مایل (Slant Column Density)
- $a_k \lambda^k$: چندجمله‌ای برای حذف اثرات پراکندگی ریلی و می

تبدیل به چگالی ستونی عمودی:

$$VCD_i = \frac{SCD_i}{AMF_i}$$

که $AMF$ (Air Mass Factor) با انتگرال‌گیری از پروفایل غلظت و هندسه خورشید محاسبه می‌شود:

$$AMF = \frac{\int_0^{z_{top}} m(z) \cdot c(z) \cdot w(z) \, dz}{\int_0^{z_{top}} c(z) \, dz}$$

#### لایه چهارم: گرانشی و ژئودتیک (Gravimetric/Geodetic)

| ماهواره | سنسور | رزولوشن | دوره | کاربرد |
|---------|--------|---------|------|--------|
| GRACE-FO | K-Band Ranging + GPS | ~300 km | ماهانه | آبخوان‌های عمیق |
| ICESat-2 | ATLAS LiDAR | 17 m footprint | 91 روز | ارتفاع برف/یخ، توپوگرافی |
| SMAP | L-Band Radiometer | 9 km | 2-3 روز | رطوبت خاک (0-5 cm) |

**فیزیک GRACE-FO (تغییرات گرانشی):**

تغییرات پتانسیل گرانشی زمین با هارمونیک‌های کروی بیان می‌شود:

$$V(r,\theta,\lambda) = \frac{GM}{r}\left[1 + \sum_{l=0}^{\infty}\sum_{m=0}^{l}\left(\frac{a}{r}\right)^l P_{lm}(\cos\theta)(C_{lm}\cos m\lambda + S_{lm}\sin m\lambda)\right]$$

تغییرات ضرایب استوکس:

$$\Delta C_{lm} = \frac{1}{4\pi} \frac{2l+1}{1+k_l'} \iint \frac{\Delta \sigma(\theta,\lambda)}{\rho_{avg} R^2} P_{lm}(\cos\theta) \cos m\lambda \, d\Omega$$

که $k_l'$ عدد لوف (Love Number) و $\Delta\sigma$ تغییرات جرم سطحی است.

### ۱.۲. الگوریتم‌های بومی استخراج داده

#### ۱.۲.۱. مدل ابری آب توسعه‌یافته (Extended Water Cloud Model)

برای استخراج رطوبت خاک از Sentinel-1:

$$\sigma^0_{total}(\theta_{inc}) = \sigma^0_{soil}(\theta_{inc}, \theta_s) \cdot \tau^2(\theta_{inc}, VWC) + \sigma^0_{veg}(\theta_{inc}, VWC)$$

اجزای مدل:

**الف) پس‌پراکندگی خاک:**
با استفاده از مدل IEM (Integral Equation Model):

$$\sigma^0_{pq} = \frac{k^2}{4\pi} e^{-2k^2\sigma_s^2\cos^2\theta} \sum_{n=1}^{\infty} |I_{pq}^n|^2 \frac{W_n(2k\sin\theta, 0)}{4k^2\sigma_s^2}$$

که:
- $k$: عدد موج ($2\pi/\lambda$)
- $\sigma_s$: انحراف معیار ارتفاع سطح خاک
- $l$: طول همبستگی سطح
- $W_n$: طیف توان ناهمواری
- $I_{pq}^n$: ضرایب فریزنل

**ب) عبور از پوشش گیاهی:**

$$\tau^2 = \exp\left(-\frac{2B \cdot VWC}{\cos\theta_{inc}}\right)$$

که $B$ ضریب ساختاری پوشش و $VWC$ محتوای آب پوشش گیاهی است.

**ج) پس‌پراکندگی پوشش گیاهی:**

$$\sigma^0_{veg} = A \cdot VWC \cdot \cos\theta_{inc} \cdot \left[1 - \exp\left(-\frac{2B \cdot VWC}{\cos\theta_{inc}}\right)\right]$$

**نوآوری بومی:** کالیبراسیون $A$ و $B$ بر اساس نوع محصول و مرحله فنولوژیکی با استفاده از یادگیری ماشین نمادین (Symbolic Regression).

#### ۱.۲.۲. حل معکوس PROSAIL برای Sentinel-2

**مدل PROSAIL** ترکیب PROSPECT (برگ) + SAIL (canopy):

**مرحله ۱: مدل برگ PROSPECT-D:**

ضریب شکست برگ:

$$n(\lambda) = n_0 + \sum_i c_i \cdot k_i(\lambda)$$

بازتاب و عبور برگ با ماتریس انتقال محاسبه می‌شود:

$$\begin{pmatrix} \tau \\ \rho \end{pmatrix} = M_{leaf}(N, C_{ab}, C_w, C_{dm}, C_{car}, \theta_{leaf})$$

**مرحله ۲: مدل canopy SAIL:**

معادلات انتقال تابش چهار-جریان (Four-Stream):

$$\frac{dL^+}{dz} = -(k+s)L^+ + s'L^- + v_1 E_s + v_2 E_d$$
$$\frac{dL^-}{dz} = (k+s)L^- - s'L^+ - v_3 E_s - v_4 E_d$$

که $L^+$ و $L^-$ تابش‌های صعودی و نزولی، $E_s$ تابش مستقیم خورشید، و $E_d$ تابش پراکنده آسمان هستند.

**حل معکوس با بهینه‌سازی:**

$$\hat{\mathbf{x}} = \arg\min_{\mathbf{x}} \sum_{\lambda \in \Lambda} w_\lambda \left[\rho_{obs}(\lambda) - \rho_{PROSAIL}(\lambda, \mathbf{x})\right]^2 + \lambda_{reg}\|\mathbf{x} - \mathbf{x}_{prior}\|^2$$

بردار حالت:

$$\mathbf{x} = [N, C_{ab}, C_w, C_{dm}, C_{car}, LAI, ALA, hot, LIDF_a, LIDF_b]^T$$

**روش حل:** الگوریتم L-BFGS-B با محدودیت‌های فیزیکی یا Bayesian MCMC برای تخمین عدم قطعیت.

#### ۱.۲.۳. الگوریتم SEBS برای تبخیر-تعرق (Sentinel-3/Landsat)

**Surface Energy Balance System:**

$$R_n = G + H + \lambda E$$

**محاسبه اجزا:**

الف) تابش خالص:
$$R_n = (1-\alpha)R_s^{\downarrow} + \varepsilon_s R_l^{\downarrow} - \varepsilon_s \sigma T_s^4$$

ب) شار گرمای خاک:
$$G = R_n \cdot \Gamma_c, \quad \Gamma_c = c_1 + c_2\alpha + c_3\alpha^2 + c_4\alpha^3$$

ج) شار گرمای محسوس (با مقاومت آیرودینامیکی):
$$H = \frac{\rho_a c_p (T_s - T_a)}{r_{ah}}$$

د) تبخیر-تعرق واقعی:
$$\lambda E = R_n - G - H$$

**محدودیت‌های فیزیکی:**
- حد خشک: $\lambda E \geq 0$
- حد تر: $\lambda E \leq R_n - G$ (با $r_{ah} = 0$)

#### ۱.۲.۴. الگوریتم Kriging برای درون‌یابی بارش (CHIRPS/GPM)

**مدل واریوگرام:**

$$\gamma(h) = \frac{1}{2N(h)}\sum_{i=1}^{N(h)} [Z(x_i) - Z(x_i + h)]^2$$

**مدل‌های واریوگرام:**

- **کروی (Spherical):**
$$\gamma(h) = \begin{cases} c_0 + c_1\left[\frac{3h}{2a} - \frac{h^3}{2a^3}\right] & h \leq a \\ c_0 + c_1 & h > a \end{cases}$$

- **نمایی (Exponential):**
$$\gamma(h) = c_0 + c_1\left[1 - e^{-h/a}\right]$$

- **گوسی (Gaussian):**
$$\gamma(h) = c_0 + c_1\left[1 - e^{-h^2/a^2}\right]$$

**Kriging ساده:**

$$\hat{Z}(x_0) = \sum_{i=1}^n \lambda_i Z(x_i)$$

با شرایط:
$$\sum \lambda_i = 1, \quad \min \text{Var}[\hat{Z} - Z]$$

سیستم معادلات Kriging:

$$\sum_j \lambda_j \gamma(x_i - x_j) + \mu = \gamma(x_i - x_0), \quad \forall i$$
$$\sum_j \lambda_j = 1$$

### ۱.۳. Data Fusion چند-سنسوری

#### ۱.۳.۱. هم‌زمانی مکانی-زمانی (Spatio-Temporal Fusion)

**مدل STARFM (Spatial and Temporal Adaptive Reflectance Fusion Model):**

$$L(x_i, y_i, t_p) = \sum_{j=1}^{M} W_j \cdot V_j \cdot \left[L(x_j, y_j, t_0) + (M(x_j,y_j,t_p) - M(x_j,y_j,t_0))\right]$$

که $W_j$ وزن مکانی، $V_j$ وزن طیفی، و $M$ تصاویر با رزولوشن متوسط هستند.

#### ۱.۳.۲. فیلتر کالمن ترکیبی (Combined Kalman Filter)

**مدل حالت:**

$$\mathbf{x}_{t+1} = A_t \mathbf{x}_t + B_t \mathbf{u}_t + \mathbf{w}_t$$

**مدل مشاهده:**

$$\mathbf{y}_t = H_t \mathbf{x}_t + \mathbf{v}_t$$

**به‌روزرسانی:**

پیش‌بینی:
$$\hat{\mathbf{x}}_{t|t-1} = A_t \hat{\mathbf{x}}_{t-1|t-1} + B_t \mathbf{u}_t$$
$$P_{t|t-1} = A_t P_{t-1|t-1} A_t^T + Q_t$$

به‌روزرسانی:
$$K_t = P_{t|t-1} H_t^T (H_t P_{t|t-1} H_t^T + R_t)^{-1}$$
$$\hat{\mathbf{x}}_{t|t} = \hat{\mathbf{x}}_{t|t-1} + K_t(\mathbf{y}_t - H_t \hat{\mathbf{x}}_{t|t-1})$$
$$P_{t|t} = (I - K_t H_t) P_{t|t-1}$$

---

## بخش دوم: موتور شبیه‌سازی فیزیکی-هیدرولوژیکی

### ۲.۱. معادله ریچاردز توسعه‌یافته (Extended Richards Equation)

**فرم مختلط (Mixed Form) با اثرات حرارتی:**

$$\frac{\partial \theta(h, T)}{\partial t} = \nabla \cdot \left[K(h,T)\left(\nabla h + \nabla z + \frac{K_T}{K_h}\nabla T\right)\right] - S_r(h, T, z)$$

**اجزای مدل:**

#### ۲.۱.۱. منحنی مشخصه خاک (Soil Water Characteristic Curve)

**مدل van Genuchten-Mualem:**

$$S_e(h) = \frac{\theta(h) - \theta_r}{\theta_s - \theta_r} = \left[1 + |\alpha h|^n\right]^{-m}$$

$$m = 1 - \frac{1}{n}, \quad n > 1$$

هدایت هیدرولیکی غیراشباع:

$$K(S_e) = K_s \cdot S_e^l \cdot \left[1 - \left(1 - S_e^{1/m}\right)^m\right]^2$$

که $l$ پارامتر انحنای منفذی (pore connectivity) است (معمولاً 0.5).

**مدل جایگزین Brooks-Corey:**

$$S_e = \begin{cases} \left(\frac{h_d}{h}\right)^\lambda & h < h_d \\ 1 & h \geq h_d \end{cases}$$

$$K(S_e) = K_s \cdot S_e^{(2+3\lambda)/\lambda}$$

#### ۲.۱.۲. هیسترزیس رطوبتی (Hysteresis)

**مدل Scott (1983):**

برای چرخه تر-خشک (wetting-drying):

$$S_e^{wet}(h) = S_e^{main}(h \cdot \beta), \quad \beta > 1$$

**مدل Mualem (1974) با نقاط بازگشت:**

$$S_e(h) = S_e^{scanning}(h; h_{reversal})$$

#### ۲.۱.۳. اثرات حرارتی (Thermal Effects)

وابستگی هدایت هیدرولیکی به دما (از طریق ویسکوزیته):

$$K(h,T) = K(h,T_{ref}) \cdot \frac{\mu(T_{ref})}{\mu(T)} \cdot \frac{\rho(T)}{\rho(T_{ref})}$$

ویسکوزیته آب (معادله Andrade):

$$\mu(T) = \mu_0 \cdot \exp\left(\frac{E_a}{R \cdot T}\right)$$

انتقال بخار آب (Philip-de Vries):

$$q_v = -D_{Tv} \nabla T - D_{\theta v} \nabla \theta$$

که:

$$D_{Tv} = \frac{D_0 \cdot a \cdot \rho_v^{sat}}{\rho_w} \cdot \frac{d\rho_v^{sat}}{dT} \cdot \eta$$

#### ۲.۱.۴. سینک ریشه (Root Water Uptake)

**مدل Feddes:**

$$S_r(h,z) = \alpha(h) \cdot b(z) \cdot T_p$$

تابع تنش:

$$\alpha(h) = \begin{cases} 0 & h > h_0 \\ \frac{h - h_0}{h_1 - h_0} & h_1 < h < h_0 \\ 1 & h_2 < h < h_1 \\ \frac{h_3 - h}{h_3 - h_2} & h_3 < h < h_2 \\ 0 & h < h_3 \end{cases}$$

توزیع عمقی ریشه (مدل Vrugt):

$$b(z) = \frac{\alpha_m}{L_r}\left[1 - \frac{z}{z_m}\right]e^{-p_z z/z_m}$$

### ۲.۲. حل عددی معادله ریچاردز

#### ۲.۲.۱. روش تفاوت محدود (Finite Difference)

**گسسته‌سازی زمانی (Implicit Euler):**

$$\frac{\theta_i^{n+1} - \theta_i^n}{\Delta t} = \frac{1}{\Delta z}\left[K_{i+1/2}^{n+1}\frac{h_{i+1}^{n+1} - h_i^{n+1} + \Delta z}{\Delta z} - K_{i-1/2}^{n+1}\frac{h_i^{n+1} - h_{i-1}^{n+1} + \Delta z}{\Delta z}\right] - S_i^{n+1}$$

**خطی‌سازی با روش Picard:**

$$C_i^{k+1} = \frac{\theta_i^{k+1} - \theta_i^k}{h_i^{k+1} - h_i^k}$$

$$\sum_j A_{ij} h_j^{k+1} = F_i^k$$

#### ۲.۲.۲. روش المان محدود (Finite Element Method)

**فرم ضعیف (Weak Form):**

$$\int_\Omega \frac{\partial \theta}{\partial t} \phi \, d\Omega + \int_\Omega K(h)\nabla h \cdot \nabla \phi \, d\Omega - \int_\Omega S_r \phi \, d\Omega = \int_{\Gamma_N} q_N \phi \, d\Gamma$$

**ماتریس‌های گسسته:**

$$\mathbf{C}(\mathbf{h})\dot{\mathbf{h}} + \mathbf{K}(\mathbf{h})\mathbf{h} = \mathbf{f}(\mathbf{h})$$

که:

$$C_{ij} = \int_\Omega C(h) N_i N_j \, d\Omega$$
$$K_{ij} = \int_\Omega K(h) \nabla N_i \cdot \nabla N_j \, d\Omega$$

#### ۲.۲.۳. شرط پایداری CFL

برای روش explicit:

$$\Delta t \leq \frac{\Delta z^2}{2D_{max}}, \quad D_{max} = \frac{K_s}{C_{min}}$$

برای روش implicit: بدون محدودیت CFL، اما نیاز به حل سیستم غیرخطی.

### ۲.۳. بیلان انرژی سطح و تبخیر-تعرق

#### ۲.۳.۱. معادله بیلان انرژی کامل

$$R_n = G + H + \lambda E + \Delta Q_{bio} + \Delta Q_{adv}$$

**اجزای دقیق:**

الف) تابش خالص:
$$R_n = (1-\alpha)R_s^{\downarrow} + \varepsilon_s R_l^{\downarrow} - \varepsilon_s \sigma T_s^4$$

ب) شار گرمای خاک (Fourier):
$$G = -k_{soil} \frac{\partial T}{\partial z}\bigg|_{z=0}$$

$$k_{soil} = \frac{k_s \cdot k_w^{\theta_w} \cdot k_a^{\theta_a}}{\theta_s}$$ (مدل de Vries)

ج) شار گرمای محسوس:
$$H = \rho_a c_p \frac{T_s - T_a}{r_{ah}}$$

د) شار گرمای نهان:
$$\lambda E = \frac{\rho_a c_p (e_s(T_s) - e_a)}{\gamma(r_{ah} + r_s)}$$

#### ۲.۳.۲. مدل Shuttleworth-Wallace (دو-منبعه)

برای تفکیک تبخیر خاک و تعرق گیاه:

$$\lambda E = \lambda E_c + \lambda E_s$$

**مقاومت‌ها:**

$$r_a^c = \frac{1}{k u_*} \ln\left(\frac{z_c - d_0}{z_c - d_0^{soil}}\right)$$

$$r_a^s = \frac{1}{k u_*} \ln\left(\frac{z_c - d_0^{soil}}{z_{0m}^{soil}}\right) + \frac{h_c}{n k u_*}$$

**مدل Medlyn برای مقاومت روزنه‌ای:**

$$g_s = g_0 + 1.6\left(1 + \frac{g_1}{\sqrt{D}}\right)\frac{A_n}{C_a}$$

**نوآوری بومی - وابستگی $g_1$ به تنش آبی:**

$$g_1(\Psi_{leaf}) = g_{1,opt} \cdot \exp\left[-\left(\frac{|\Psi_{leaf}|}{|\Psi_{50}|}\right)^c\right]$$

که $\Psi_{50}$ پتانسیل آبی برای از دست دادن 50% هدایت هیدرولیکی آوند چوبی است.

#### ۲.۳.۳. مدل Penman-Monteith (FAO-56)

$$ET_0 = \frac{0.408\Delta(R_n - G) + \gamma \frac{900}{T+273}u_2(e_s - e_a)}{\Delta + \gamma(1 + 0.34u_2)}$$

**ضرایب محصول (Crop Coefficients):**

$$ET_c = K_c \cdot ET_0$$

$$K_c = K_{cb} + K_e$$

که $K_{cb}$ ضریب پایه محصول و $K_e$ ضریب تبخیر خاک است.

### ۲.۴. هیدرولوژی سطحی - معادلات Saint-Venant

#### ۲.۴.۱. فرم کامل (Full Dynamic Wave)

**بقای جرم:**
$$\frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = q_L$$

**بقای مومنتوم:**
$$\frac{\partial Q}{\partial t} + \frac{\partial}{\partial x}\left(\beta\frac{Q^2}{A}\right) + gA\frac{\partial h}{\partial x} + gA(S_f - S_0) = 0$$

که:
- $A$: سطح مقطع جریان
- $Q$: دبی
- $\beta$: ضریب کوریولیس (توزیع سرعت)
- $S_f$: شیب اصطکاکی
- $S_0$: شیب بستر
- $q_L$: ورودی جانبی

#### ۲.۴.۲. تقریب‌های ساده‌شده

**موج سینماتیک (Kinematic Wave):**
$$\frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = q_L, \quad Q = \alpha A^m$$

**موج انتشار (Diffusive Wave):**
$$\frac{\partial Q}{\partial t} + c\frac{\partial Q}{\partial x} = D\frac{\partial^2 Q}{\partial x^2} + q_L$$

که $c = dQ/dA$ سرعت موج و $D = Q/(2BS_0)$ ضریم انتشار.

#### ۲.۴.۳. روش SCS-CN برای رواناب

$$Q = \begin{cases} \frac{(P - I_a)^2}{(P - I_a) + S} & P > I_a \\ 0 & P \leq I_a \end{cases}$$

$$S = \frac{25400}{CN} - 254, \quad I_a = 0.2S$$

**جدول CN بومی بر اساس خاک‌های ایران:**

| گروه هیدرولوژیکی خاک | کاربری | CN خشک | CN متوسط | CN مرطوب |
|----------------------|--------|--------|----------|----------|
| A (شنی) | جنگل | 30 | 45 | 66 |
| A | زراعت دیم | 54 | 67 | 81 |
| B (لوم) | جنگل | 48 | 60 | 76 |
| B | زراعت دیم | 67 | 78 | 87 |
| C (لوم-رسی) | جنگل | 62 | 73 | 83 |
| C | زراعت دیم | 76 | 85 | 92 |
| D (رسی) | مرتع | 71 | 80 | 87 |
| D | زراعت آبی | 81 | 88 | 94 |

### ۲.۵. انتقال حرارت در خاک

#### ۲.۵.۱. معادله فوریه با منابع:

$$C_{soil}\frac{\partial T}{\partial t} = \nabla \cdot (k_{eff} \nabla T) + Q_{latent} + Q_{bio}$$

**ظرفیت حرارتی خاک:**

$$C_{soil} = \theta_w c_w + \theta_s c_s + \theta_a c_a + \theta_{om} c_{om}$$

**هدایت حرارتی مؤثر (de Vries):**

$$k_{eff} = \frac{\sum_i k_i \theta_i K_i}{\sum_i \theta_i K_i}$$

که $K_i$ ضریب وزن‌دهی دمای هر جزء است.

---

## بخش سوم: موتور بیوژئوشیمی و شیمی خاک

### ۳.۱. دینامیک کربن خاک - مدل ۷-مخزنه

#### ۳.۱.۱. ساختار مخازن

$$\frac{dC_i}{dt} = I_i(t) - k_i \cdot \xi(T,\theta,O_2,pH) \cdot C_i + \sum_{j \neq i} \epsilon_{ji} k_j C_j$$

**مخازن و نیمه‌عمرها:**

| مخزن | نماد | نیمه‌عمر | منبع اصلی |
|------|------|----------|-----------|
| متابولیک | MET | 0.1-0.5 سال | بقایای تازه |
| ساختاری | STR | 1-5 سال | سلولز، لیگنین |
| فعال | ACT | 0.5-2 سال | میکروبیوم |
| کند | SLOW | 20-50 سال | هو مین نیمه‌پایدار |
| پایدار | PASS | 200-1500 سال | هو مین پایدار |
| محلول | DOC | روزانه | شستشوی کربن |
| بیوچار | BC | 100-5000 سال | پیرولیز |

#### ۳.۱.۲. توابع تعدیل محیطی

**تابع دما (سه‌بخشی):**

$$\xi_T(T) = \begin{cases} 0 & T < T_{min} \\ \exp\left[\frac{E_a}{R}\left(\frac{1}{T_{ref}} - \frac{1}{T}\right)\right] & T_{min} \leq T \leq T_{opt} \\ \xi_T(T_{opt}) \cdot \exp\left[-\frac{(T-T_{opt})^2}{2\sigma_T^2}\right] & T > T_{opt} \end{cases}$$

**تابع رطوبت:**

$$\xi_\theta(\theta) = \begin{cases} 0.2 \cdot \frac{\theta}{\theta_{fc}} & 0 \leq \theta \leq \theta_{fc} \\ 0.2 + 0.8\frac{\theta_s - \theta}{\theta_s - \theta_{fc}} & \theta_{fc} < \theta \leq \theta_s \\ 0.6 & \theta > \theta_s \text{ (بی‌هوازی)} \end{cases}$$

**تابع اکسیژن:**

$$\xi_{O_2} = \frac{[O_2]}{K_{O_2} + [O_2]}$$

**تابع pH:**

$$\xi_{pH} = \exp\left[-\frac{(pH - pH_{opt})^2}{2\sigma_{pH}^2}\right]$$

#### ۳.۱.۳. ضرایب انتقال بین مخازن

| از → به | MET | STR | ACT | SLOW | PASS |
|---------|-----|-----|-----|------|------|
| MET | - | 0.45 | 0.55 | 0 | 0 |
| STR | 0.20 | - | 0.30 | 0.45 | 0.05 |
| ACT | 0 | 0 | - | 0.40 | 0.15 |
| SLOW | 0 | 0 | 0.30 | - | 0.30 |
| PASS | 0 | 0 | 0.10 | 0.15 | - |

### ۳.۲. چرخه نیتروژن

#### ۳.۲.۱. معدنی‌شدن (Mineralization)

$$\frac{dN_{min}}{dt} = \sum_i k_i \cdot C_i \cdot (C:N)^{-1} \cdot \xi(T,\theta) - N_{imm}$$

**شرط معدنی‌شدن vs. تثبیت:**
- اگر $C:N < 25$: معدنی‌شدن خالص (آزادسازی $NH_4^+$)
- اگر $C:N > 25$: تثبیت خالص (مصرف $NH_4^+$ توسط میکروب‌ها)

#### ۳.۲.۲. نیتریفیکاسیون

$$NH_4^+ + 1.5O_2 \xrightarrow{AOB} NO_2^- + 2H^+ + H_2O$$
$$NO_2^- + 0.5O_2 \xrightarrow{NOB} NO_3^-$$

**سینتیک Monod:**

$$r_{nit} = \mu_{max} \cdot \frac{[NH_4^+]}{K_{NH_4} + [NH_4^+]} \cdot \frac{[O_2]}{K_{O_2} + [O_2]} \cdot f(T) \cdot f(pH)$$

#### ۳.۲.۳. دنیتریفیکاسیون

$$NO_3^- \rightarrow NO_2^- \rightarrow NO \rightarrow N_2O \rightarrow N_2$$

**شرط فعال‌سازی:** $\theta > 0.8\theta_s$ (بی‌هوازی)

$$r_{denit} = k_{denit} \cdot [NO_3^-] \cdot DOC \cdot \xi(T) \cdot \xi_{anaerobic}$$

**نسبت $N_2O/N_2$:**

$$\frac{[N_2O]}{[N_2]} = f(pH, [NO_3^-], C:N)$$

#### ۳.۲.۴. آبشویی نیتروژن

$$N_{leach} = \int_0^L q_w(z) \cdot C_{NO_3}(z) \, dz$$

که $q_w$ شار آب و $C_{NO_3}$ غلظت نیترات محلول است.

### ۳.۳. شیمی محلول خاک و تبادل یونی

#### ۳.۳.۱. ظرفیت تبادل کاتیونی (CEC)

$$CEC = \frac{\sum_i [M_i^{n+}]_{exch} \cdot n}{\text{وزن خاک خشک}} \quad (\text{cmol}_c/\text{kg})$$

**مدل‌سازی تبادل یونی (Gapon):**

$$\frac{[Ca-X] \cdot [K^+]_{sol}}{[K-X] \cdot [Ca^{2+}]_{sol}^{1/2}} = K_G$$

**مدل Vanselow:**

$$K_V = \frac{[Na-X]^2 \cdot [Ca^{2+}]_{sol}}{[Ca-X] \cdot [Na^+]_{sol}^2}$$

#### ۳.۳.۲. معادله Nernst-Planck

$$J_i = -D_i \nabla C_i - \frac{z_i F}{RT} D_i C_i \nabla \Phi + C_i \mathbf{v}$$

اجزا:
- ترم اول: انتشار (Fick)
- ترم دوم: مهاجرت الکتریکی
- ترم سوم: همرفت (advection)

**شرط الکتروخنثی:**

$$\sum_i z_i C_i = 0$$

#### ۳.۳.۳. ایزوترم‌های جذب

**لانگمویر:**
$$q = \frac{q_{max} K_L C}{1 + K_L C}$$

**فروندلیچ:**
$$q = K_F C^{1/n}$$

**سیپس (Sips) - مناسب خاک‌های آهکی ایران:**
$$q = \frac{q_{max} (K C)^n}{1 + (K C)^n}$$

**تمکین (Temkin):**
$$q = \frac{RT}{b_T} \ln(K_T C)$$

### ۳.۴. شوری و سدیمی شدن خاک

#### ۳.۴.۱. معادله شستشو (Leaching Fraction)

$$LF = \frac{D_{dw}}{D_{iw}} = \frac{EC_{iw}}{EC_{dw}}$$

**رابطه EC با شوری:**

$$EC_e = \frac{EC_{sat} \cdot \theta_{sat}}{\theta_e}$$

#### ۳.۴.۲. نسبت جذب سدیم (SAR)

$$SAR = \frac{[Na^+]}{\sqrt{\frac{[Ca^{2+}] + [Mg^{2+}]}{2}}}$$

**مدل پیش‌بینی ESP از SAR:**

$$ESP = \frac{100 \cdot SAR}{1 + SAR} \quad (\text{تقریب خطی})$$

یا مدل دقیق‌تر:

$$ESP = \frac{100 \cdot K_x \cdot SAR}{1 + K_x \cdot SAR}$$

#### ۳.۴.۳. اثر شوری بر رشد گیاه

$$Y_r = \begin{cases} 1 & EC_e \leq EC_{threshold} \\ 1 - s(EC_e - EC_{threshold}) & EC_e > EC_{threshold} \end{cases}$$

که $s$ شیب کاهش عملکرد و $EC_{threshold}$ آستانه تحمل محصول است.

---

## بخش چهارم: پارادایم‌های محاسباتی نوین

### ۴.۱. شبکه‌های عصبی آگاه از فیزیک (Physics-Informed Neural Networks)

#### ۴.۱.۱. فرمول‌بندی کلی

**شبکه عصبی:** $\hat{u}(\mathbf{x}, t; \boldsymbol{\theta})$

**تابع هزینه ترکیبی:**

$$\mathcal{L} = \lambda_1 \mathcal{L}_{data} + \lambda_2 \mathcal{L}_{PDE} + \lambda_3 \mathcal{L}_{BC} + \lambda_4 \mathcal{L}_{IC}$$

**اجزا:**

$$\mathcal{L}_{data} = \frac{1}{N_d}\sum_{i=1}^{N_d}\left\|u_{obs}(\mathbf{x}_i, t_i) - \hat{u}(\mathbf{x}_i, t_i; \boldsymbol{\theta})\right\|^2$$

$$\mathcal{L}_{PDE} = \frac{1}{N_f}\sum_{i=1}^{N_f}\left\|\mathcal{N}[\hat{u}](\mathbf{x}_i, t_i; \boldsymbol{\theta})\right\|^2$$

که $\mathcal{N}[\cdot]$ اپراتور دیفرانسیلی معادله حاکم است.

#### ۴.۱.۲. کاربرد در معادله ریچاردز

$$\mathcal{L}_{PDE} = \frac{1}{N_f}\sum_{i=1}^{N_f}\left\|\frac{\partial \hat{\theta}}{\partial t} - \nabla \cdot [K(\hat{h})\nabla(\hat{h} + z)] + S_r\right\|^2$$

**محاسبه مشتقات با Automatic Differentiation:**

$$\frac{\partial \hat{\theta}}{\partial t} = \frac{\partial \hat{\theta}}{\partial t}\bigg|_{\text{AutoGrad}}$$

$$\nabla^2 \hat{h} = \sum_{d=1}^{D} \frac{\partial^2 \hat{h}}{\partial x_d^2}$$

#### ۴.۱.۳. حل معکوس (Inverse Problem)

**تخمین پارامترهای خاک:**

$$\hat{\boldsymbol{\phi}} = \arg\min_{\boldsymbol{\phi}} \mathcal{L}(\boldsymbol{\theta}, \boldsymbol{\phi})$$

که $\boldsymbol{\phi} = [\alpha, n, K_s, \theta_r, \theta_s, l]$ پارامترهای van Genuchten هستند.

**روش:** آموزش هم‌زمان شبکه عصبی و پارامترها با بهینه‌سازی ترکیبی.

#### ۴.۱.۴. معماری شبکه

**لایه‌ها:**
- ورودی: $(z, t)$ یا $(x, y, z, t)$
- لایه‌های پنهان: 8-12 لایه با 64-256 نورون
- فعال‌سازی: $\tanh$ یا $\sin$ (برای تقریب توابع نوسانی)
- خروجی: $\hat{\theta}$, $\hat{h}$, $\hat{T}$

**نرمال‌سازی:**

$$\hat{z} = \frac{z - z_{min}}{z_{max} - z_{min}} \cdot 2 - 1$$

### ۴.۲. الگوریتم بهینه‌سازی کوانتومی-الهام (QAOA-Inspired)

#### ۴.۲.۱. فرمول‌بندی QUBO

**مسئله:** تخصیص بهینه آب به $n$ مزرعه با $T$ بازه زمانی

$$\min_{\mathbf{x}} \sum_{i=1}^n \sum_{t=1}^T c_{it} x_{it} + \sum_{i<j} \sum_{t} J_{ij} x_{it} x_{jt}$$

$$\text{s.t.} \quad \sum_i x_{it} \leq W_t \quad \forall t$$

**تبدیل به QUBO با جریمه:**

$$H(\mathbf{x}) = \sum_{i,t} c_{it} x_{it} + \sum_{i<j,t} J_{ij} x_{it}x_{jt} + P\sum_t\left(\sum_i x_{it} - W_t\right)^2$$

که $P$ ضریب جریمه بزرگ است.

#### ۴.۲.۲. الگوریتم QAOA

**حالت کوانتومی:**

$$|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{p=1}^{P} e^{-i\beta_p B} e^{-i\gamma_p C} |+\rangle^{\otimes n}$$

که:
- $C = \sum_{i<j} J_{ij} Z_i Z_j + \sum_i h_i Z_i$ (Hamiltonian هزینه)
- $B = \sum_i X_i$ (Hamiltonian میکسر)
- $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$

**بهینه‌سازی کلاسیکی:**

$$(\boldsymbol{\gamma}^*, \boldsymbol{\beta}^*) = \arg\min_{\boldsymbol{\gamma}, \boldsymbol{\beta}} \langle \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) | C | \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle$$

#### ۴.۲.۳. پیاده‌سازی کلاسیکی (Simulated Annealing)

**الگوریتم:**

1. شروع با $\mathbf{x}_0$ تصادفی و دمای $T_0$
2. برای هر تکرار:
   - انتخاب همسایه $\mathbf{x}'$ (فلیپ یک بیت)
   - $\Delta E = H(\mathbf{x}') - H(\mathbf{x})$
   - اگر $\Delta E < 0$ یا $r < e^{-\Delta E / T}$: قبول
3. کاهش دما: $T_{k+1} = \alpha T_k$ ($\alpha \approx 0.95$)
4. تکرار تا همگرایی

### ۴.۳. رمزنگاری پسا-کوانتومی (Post-Quantum Cryptography)

#### ۴.۳.۱. CRYSTALS-Kyber (ML-KEM)

**مبنای ریاضی:** مسئله Learning With Errors (LWE)

$$\mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e} \pmod{q}$$

که:
- $\mathbf{A} \in R_q^{k \times k}$: ماتریس عمومی تصادفی
- $\mathbf{s}, \mathbf{e} \in R_q^k$: بردارهای مخفی و خطا
- $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$: حلقه چندجمله‌ای

**پارامترها:**

| سطح | Kyber-512 | Kyber-768 | Kyber-1024 |
|------|-----------|-----------|------------|
| امنیت | 128-bit | 192-bit | 256-bit |
| $n$ | 256 | 256 | 256 |
| $q$ | 3329 | 3329 | 3329 |
| $k$ | 2 | 3 | 4 |
| اندازه کلید عمومی | 800 B | 1184 B | 1568 B |

#### ۴.۳.۲. CRYSTALS-Dilithium (ML-DSA)

برای امضای دیجیتال داده‌های ماهواره‌ای:

**تولید کلید:**
1. $\mathbf{A} \leftarrow R_q^{k \times l}$
2. $\mathbf{s}_1, \mathbf{s}_2 \leftarrow \chi_\eta$ (توزیع باینومی مرکزی)
3. $\mathbf{t} = \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2$

**امضا:**
1. $\mathbf{y} \leftarrow \chi_\gamma$
2. $\mathbf{w} = \mathbf{A}\mathbf{y}$
3. $c = H(\mu \| \mathbf{w})$
4. $\mathbf{z} = \mathbf{y} + c\mathbf{s}_1$
5. اگر $\|\mathbf{z}\|_\infty \geq \gamma - \beta$: رد و تکرار

#### ۴.۳.۳. SPHINCS+ (Hash-Based)

برای تأیید اصالت داده‌های حساس (fallback امن):

- مبتنی بر توابع هش (بدون نیاز به مسائل جبری)
- امنیت فقط به مقاومت هش در برابر برخورد وابسته است
- اندازه امضا: 8-49 KB
- مناسب برای تأیید یک‌باره (one-time) داده‌های ماهواره‌ای

### ۴.۴. یادگیری فدرال (Federated Learning)

#### ۴.۴.۱. الگوریتم FedAvg

**هدف:**

$$\min_{\mathbf{w}} F(\mathbf{w}) = \sum_{k=1}^K \frac{n_k}{n} F_k(\mathbf{w})$$

**الگوریتم:**

1. سرور $\mathbf{w}_0$ را به $K$ کلاینت ارسال می‌کند
2. هر کلاینت $k$:
   - $\mathbf{w}_{k}^{t+1} \leftarrow \mathbf{w}_k^t - \eta \nabla F_k(\mathbf{w}_k^t)$ (چند مرحله SGD محلی)
3. سرور:
   - $\mathbf{w}^{t+1} = \sum_{k=1}^K \frac{n_k}{n} \mathbf{w}_k^{t+1}$
4. تکرار تا همگرایی

#### ۴.۴.۲. امنیت با Differential Privacy

$$\mathbf{w}_k^{t+1} \leftarrow \text{Clip}(\mathbf{w}_k^{t+1}, C) + \mathcal{N}(0, \sigma^2 C^2 \mathbf{I})$$

که $C$ norm clipping و $\sigma$ پارامتر نویز است.

**تضمین حریم خصوصی $(\varepsilon, \delta)$-DP:**

$$\Pr[\mathcal{M}(D) \in S] \leq e^\varepsilon \Pr[\mathcal{M}(D') \in S] + \delta$$

---

## بخش پنجم: هواشناسی و اقلیم‌شناسی

### ۵.۱. دینامیک لایه مرزی سطح (Surface Boundary Layer)

#### ۵.۱.۱. معادلات ناویر-استوکس میانگین‌گیری رینولدز (RANS)

**بقای جرم:**
$$\frac{\partial \bar{u}_i}{\partial x_i} = 0$$

**بقای مومنتوم:**
$$\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j \frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu \nabla^2 \bar{u}_i - \frac{\partial \tau_{ij}}{\partial x_j} + g_i$$

که $\tau_{ij} = \overline{u_i' u_j'}$ تانسور تنش رینولدز است.

#### ۵.۱.۲. مدل آشفتگی k-ε

**معادله انرژی جنبشی آشفتگی:**

$$\frac{\partial k}{\partial t} + \bar{u}_j \frac{\partial k}{\partial x_j} = \frac{\partial}{\partial x_j}\left[\left(\nu + \frac{\nu_t}{\sigma_k}\right)\frac{\partial k}{\partial x_j}\right] + P_k + P_b - \varepsilon$$

**معادله نرخ اتلاف:**

$$\frac{\partial \varepsilon}{\partial t} + \bar{u}_j \frac{\partial \varepsilon}{\partial x_j} = \frac{\partial}{\partial x_j}\left[\left(\nu + \frac{\nu_t}{\sigma_\varepsilon}\right)\frac{\partial \varepsilon}{\partial x_j}\right] + C_{\varepsilon 1}\frac{\varepsilon}{k}(P_k + C_{\varepsilon 3}P_b) - C_{\varepsilon 2}\frac{\varepsilon^2}{k}$$

**ثوابت استاندارد:**

| پارامتر | مقدار |
|---------|-------|
| $C_\mu$ | 0.09 |
| $C_{\varepsilon 1}$ | 1.44 |
| $C_{\varepsilon 2}$ | 1.92 |
| $\sigma_k$ | 1.0 |
| $\sigma_\varepsilon$ | 1.3 |

**ویسکوزیته آشفتگی:**

$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

#### ۵.۱.۳. طول مونین-اوبوخوف (Monin-Obukhov Length)

$$L = -\frac{u_*^3 T_{air}}{k g \overline{w'T'_v}}$$

که:
- $u_* = (\tau_0/\rho)^{1/2}$: سرعت اصطکاکی
- $k = 0.41$: ثابت فون کارمان
- $\overline{w'T'_v}$: شار حرارتی مجازی

**توابع پایداری:**

برای شرایط ناپایدار ($z/L < 0$):

$$\phi_m(\zeta) = (1 - 16\zeta)^{-1/4}$$
$$\phi_h(\zeta) = (1 - 16\zeta)^{-1/2}$$

برای شرایط پایدار ($z/L > 0$):

$$\phi_m(\zeta) = 1 + 5\zeta$$
$$\phi_h(\zeta) = 1 + 5\zeta$$

### ۵.۲. مدل‌سازی میکروکلیما

#### ۵.۲.۱. بیلان انرژی canopy

$$R_n^c + R_n^s = H_c + H_s + \lambda E_c + \lambda E_s + G$$

#### ۵.۲.۲. انتقال حرارت و جرم درون canopy

**پروفیل سرعت باد:**

$$u(z) = \frac{u_*}{k} \ln\left(\frac{z-d}{z_0}\right)$$

که $d$ ارتفاع جابجایی و $z_0$ طول زبری است.

**ضریب تبادل جرم:**

$$g_b = \frac{0.135 \cdot u(z)}{d_{leaf}} \cdot Sc^{-2/3}$$

که $Sc$ عدد اشمیت است.

### ۵.۳. اقلیم‌شناسی و پیش‌بینی بلندمدت

#### ۵.۳.۱. شاخص‌های تلکانکتیو

**ENSO (El Niño-Southern Oscillation):**

$$ONI = \frac{1}{3}\sum_{i=-1}^{1} SST'_{i}(3.4)$$

- $ONI > +0.5$: El Niño
- $ONI < -0.5$: La Niña

**NAO (North Atlantic Oscillation):**

$$NAO = \frac{P'_{Azores} - P'_{Iceland}}{\sigma}$$

**IOD (Indian Ocean Dipole):**

$$DMI = SST'_{west} - SST'_{east}$$

#### ۵.۳.۲. زنجیره مارکوف پنهان (HMM)

**مدل:**

$$P(S_t = j | S_{t-1} = i) = a_{ij}$$
$$P(O_t | S_t = j) = b_j(O_t)$$

**الگوریتم Baum-Welch:**

E-step:
$$\xi_t(i,j) = \frac{\alpha_t(i) a_{ij} b_j(O_{t+1}) \beta_{t+1}(j)}{\sum_i \sum_j \alpha_t(i) a_{ij} b_j(O_{t+1}) \beta_{t+1}(j)}$$

M-step:
$$\hat{a}_{ij} = \frac{\sum_{t=1}^{T-1} \xi_t(i,j)}{\sum_{t=1}^{T-1} \gamma_t(i)}$$

#### ۵.۳.۳. Downscaling آماری

**مدل رگرسیون چندمتغیره:**

$$Y_{local} = \beta_0 + \sum_k \beta_k X_k^{GCM} + \varepsilon$$

**مدل‌های پیشرفته:**

- **Random Forest:**
$$\hat{Y} = \frac{1}{B}\sum_{b=1}^B T_b(\mathbf{X})$$

- **CNN-LSTM:**
$$\mathbf{h}_t = \text{LSTM}(\text{CNN}(\mathbf{X}_{t-w:t}))$$

---

## بخش ششم: جامعه‌شناسی، اقتصاد و توسعه

### ۶.۱. نظریه بازی‌ها و منابع مشترک

#### ۶.۱.۱. بازی منابع مشترک (Common-Pool Resource Game)

**تابع سود کشاورز $i$:**

$$\pi_i(x_i, \mathbf{x}_{-i}) = B(x_i) - C(X) \cdot x_i - \tau_i x_i$$

که $X = \sum_j x_j$ برداشت کل و $\tau_i$ مالیات/یارانه است.

**شرط بهینه اجتماعی:**

$$B'(x^*) = C'(X^*) \cdot x^* + C(X^*)$$

**شرط بهینه فردی (Nash):**

$$B'(x_i^{NE}) = C'(X^{NE}) \cdot x_i^{NE} + C(X^{NE})$$

**تراژدی منابع مشترک:** $X^{NE} > X^*$ (برداشت بیش از حد)

#### ۶.۱.۲. دینامیک تکاملی (Replicator Dynamics)

$$\dot{x}_i = x_i [f_i(\mathbf{x}) - \bar{f}(\mathbf{x})]$$

که:
- $x_i$: فراوانی استراتژی $i$
- $f_i$: برازش استراتژی $i$
- $\bar{f} = \sum_j x_j f_j$: برازش میانگین

**تحلیل پایداری:**

نقطه تعادل $x^*$ پایدار است اگر:

$$\frac{d\dot{x}}{dx}\bigg|_{x^*} < 0$$

#### ۶.۱.۳. مکانیزم‌های طراحی

**مالیات پیگوین:**

$$\tau^* = C'(X^*) \cdot x^*$$

**قرارداد همکاری:**

$$U_i = \pi_i + \beta \cdot \mathbb{1}_{\{x_i \leq x^{coop}\}} - \gamma \cdot \mathbb{1}_{\{x_i > x^{coop}\}}$$

**شرط پایداری همکاری:**

$$\beta > \gamma \cdot \frac{1-\delta}{\delta}$$

که $\delta$ عامل تنزیل است.

### ۶.۲. اقتصادسنجی

#### ۶.۲.۱. تابع تولید Cobb-Douglas توسعه‌یافته

$$Y_t = A_t \cdot K_t^\alpha \cdot L_t^\beta \cdot W_t^\gamma \cdot S_t^\delta \cdot C_t^\epsilon \cdot e^{-\lambda D_t}$$

**لاگاریتم‌گیری:**

$$\ln Y_t = \ln A_t + \alpha \ln K_t + \beta \ln L_t + \gamma \ln W_t + \delta \ln S_t + \epsilon \ln C_t - \lambda D_t$$

**شرایط:**
- $\alpha + \beta + \gamma + \delta + \epsilon = 1$ (بازده ثابت)
- $\alpha, \beta, \gamma, \delta, \epsilon > 0$
- $\lambda > 0$ (اثر منفی خشکسالی)

#### ۶.۲.۲. مدل تعادل عمومی محاسباتی (CGE)

**بهینه‌سازی مصرف‌کننده:**

$$\max_{C,L} U(C,L) = \sum_{t=0}^T \beta^t u(C_t, L_t)$$

**محدودیت‌ها:**

$$P_t C_t = w_t L_t + r_t K_t + T_t$$

$$K_{t+1} = (1-\delta)K_t + I_t$$

$$W_{t+1} = W_t + R_t - \sum_i w_i Y_{i,t} - ET_t$$

#### ۶.۲.۳. تحلیل هزینه-فایده (CBA)

$$NPV = \sum_{t=0}^T \frac{B_t - C_t}{(1+r)^t}$$

**نرخ تنزیل اجتماعی:**

$$r = \rho + \eta \cdot g$$

که:
- $\rho$: نرخ ترجیح زمانی خالص (1-2%)
- $\eta$: کشش نهایی مصرف (1-2)
- $g$: نرخ رشد سرانه (2-3%)

**قیمت سایه کربن:**

$$SCC = \sum_{t=0}^T \frac{\partial D_t}{\partial E} \cdot \frac{1}{(1+r)^t}$$

### ۶.۳. توسعه روستایی و رویکرد قابلیت‌ها

#### ۶.۳.۱. شاخص قابلیت (Capability Index)

$$CI = \sum_{k=1}^K w_k \cdot f_k(\mathbf{x}_k)$$

**ابعاد:**

| بُعد | شاخص‌ها | وزن پیشنهادی |
|------|---------|--------------|
| آزادی اقتصادی | تنوع درآمد، دسترسی به بازار، بیمه | 0.25 |
| تاب‌آوری اقلیمی | تنوع محصول، ذخیره آب، هشدار زودهنگام | 0.25 |
| دانش و فناوری | آموزش، دسترسی به اطلاعات، نوآوری | 0.20 |
| سرمایه اجتماعی | شبکه‌های همکاری، اعتماد، مشارکت | 0.15 |
| سلامت اکوسیستم | کیفیت خاک، تنوع زیستی، آب | 0.15 |

#### ۶.۳.۲. منطق فازی

**توابع عضویت:**

$$\mu_A(x) = \begin{cases} 0 & x \leq a \\ \frac{x-a}{b-a} & a < x < b \\ 1 & x \geq b \end{cases}$$

**قواعد استنتاج:**

- IF آب = کم AND دانش = بالا THEN تاب‌آوری = متوسط
- IF کربن = زیاد AND بازار = فعال THEN درآمد = بالا
- IF شوری = زیاد AND شستشو = کم THEN عملکرد = پایین

**Defuzzification (مرکز ثقل):**

$$z^* = \frac{\int z \cdot \mu(z) \, dz}{\int \mu(z) \, dz}$$

---

## بخش هفتم: یکپارچه‌سازی چند-مقیاسی

### ۷.۱. سلسله مراتب مقیاس‌ها

| مقیاس | اندازه | پدیده غالب | مدل | روش عددی |
|--------|--------|-------------|------|----------|
| مولکولی | nm-μm | واکنش‌های شیمیایی | سینتیک آرنیوس | ODE |
| خاکدانه | mm-cm | انتقال آب و یون | ریچاردز + Nernst-Planck | FDM |
| پروفیل خاک | m | بیوژئوشیمی | DayCent | ODE |
| مزرعه | ha | بیلان انرژی، رشد | Shuttleworth-Wallace | PDE |
| حوضه آبریز | km² | هیدرولوژی سطحی | Saint-Venant | FVM |
| منطقه‌ای | 100 km | اقلیم، تلکانکتیو | WRF, HMM | Spectral |
| جهانی | 1000+ km | چرخه‌های بیوژئوشیمی | ESM | GCM |

### ۷.۲. تکنیک‌های Upscaling

#### ۷.۲.۱. همگن‌سازی مؤثر

**هدایت هیدرولیکی مؤثر:**

$$K_{eff} = \exp\left(\frac{1}{V}\int_V \ln K(\mathbf{x}) \, dV\right)$$

(میانگین هندسی برای محیط‌های ناهمگن)

**پراکندگی مؤثر:**

$$D_{eff} = D_0 + \alpha_L v$$

که $\alpha_L$ پراکندگی طولی و $v$ سرعت دارسی است.

#### ۷.۲.۲. Geographically Weighted Regression (GWR)

$$y_i = \beta_0(u_i,v_i) + \sum_k \beta_k(u_i,v_i) x_{ik} + \varepsilon_i$$

**تخمین محلی:**

$$\hat{\boldsymbol{\beta}}(u_i,v_i) = (\mathbf{X}^T \mathbf{W}(i) \mathbf{X})^{-1} \mathbf{X}^T \mathbf{W}(i) \mathbf{y}$$

که $\mathbf{W}(i)$ ماتریس وزن‌دهی مکانی است:

$$W_{ij} = \exp\left(-\frac{d_{ij}^2}{2h^2}\right)$$

---

## بخش هشتم: تحلیل عدم قطعیت و اعتبارسنجی

### ۸.۱. منابع عدم قطعیت

1. **پارامتری:** مقادیر $K_s$, $\alpha$, $n$ در مدل van Genuchten
2. **ساختاری:** انتخاب مدل (Richards vs. Green-Ampt vs. Bucket)
3. **داده‌های ورودی:** خطاهای ماهواره‌ای و ایستگاهی
4. **سناریو:** مسیرهای اقلیمی آینده (RCPs/SSPs)
5. **مشاهده‌ای:** خطای اندازه‌گیری سنسورها

### ۸.۲. روش‌های انتشار عدم قطعیت

#### ۸.۲.۱. مونت کارلو

$$\hat{E}[Y] = \frac{1}{N}\sum_{i=1}^N f(\boldsymbol{\theta}_i), \quad \boldsymbol{\theta}_i \sim p(\boldsymbol{\theta})$$

$$\hat{\text{Var}}[Y] = \frac{1}{N-1}\sum_{i=1}^N (f(\boldsymbol{\theta}_i) - \hat{E}[Y])^2$$

**تعداد نمونه مورد نیاز:** $N \geq 10^4$ برای تخمین دقیق

#### ۸.۲.۲. Polynomial Chaos Expansion (PCE)

$$Y(\boldsymbol{\xi}) \approx \sum_{|\boldsymbol{\alpha}| \leq p} c_{\boldsymbol{\alpha}} \Psi_{\boldsymbol{\alpha}}(\boldsymbol{\xi})$$

که $\Psi_{\boldsymbol{\alpha}}$ چندجمله‌ای‌های متعامد هستند:
- Hermite برای توزیع نرمال
- Legendre برای توزیع یکنواخت
- Laguerre برای توزیع گاما

**تخمین ضرایب:**

$$c_{\boldsymbol{\alpha}} = \frac{\langle Y, \Psi_{\boldsymbol{\alpha}} \rangle}{\langle \Psi_{\boldsymbol{\alpha}}, \Psi_{\boldsymbol{\alpha}} \rangle} \approx \frac{1}{N}\sum_{i=1}^N Y(\boldsymbol{\xi}_i) \Psi_{\boldsymbol{\alpha}}(\boldsymbol{\xi}_i)$$

#### ۸.۲.۳. Ensemble Kalman Filter (EnKF)

**Forecast Step:**

$$\mathbf{x}_{t+1}^f = M(\mathbf{x}_t^a) + \mathbf{w}_t$$

**Analysis Step:**

$$\mathbf{x}_t^a = \mathbf{x}_t^f + K_t (\mathbf{y}_t - H\mathbf{x}_t^f)$$

$$K_t = P_t^f H^T (HP_t^f H^T + R)^{-1}$$

**نسخه Ensemble:**

$$K_t = \frac{1}{N_e-1} \mathbf{X}_f' \mathbf{Y}_f'^T \left(\frac{1}{N_e-1}\mathbf{Y}_f' \mathbf{Y}_f'^T + R\right)^{-1}$$

### ۸.۳. معیارهای اعتبارسنجی

| معیار | فرمول | مقدار ایده‌آل |
|-------|-------|---------------|
| NSE | $1 - \frac{\sum(O-S)^2}{\sum(O-\bar{O})^2}$ | 1 |
| RMSE | $\sqrt{\frac{1}{n}\sum(O-S)^2}$ | 0 |
| $R^2$ | $\left[\frac{\sum(O-\bar{O})(S-\bar{S})}{\sqrt{\sum(O-\bar{O})^2\sum(S-\bar{S})^2}}\right]^2$ | 1 |
| PBIAS | $100 \cdot \frac{\sum(S-O)}{\sum O}$ | 0 |
| KGE | $1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}$ | 1 |
| MAE | $\frac{1}{n}\sum|O-S|$ | 0 |

### ۸.۴. تحلیل حساسیت سراسری

#### ۸.۴.۱. شاخص‌های سوبول

**اثر مرتبه اول:**

$$S_i = \frac{V_{X_i}[E_{X_{\sim i}}(Y|X_i)]}{V(Y)}$$

**اثر کل:**

$$S_{Ti} = \frac{E_{X_{\sim i}}[V_{X_i}(Y|X_{\sim i})]}{V(Y)} = 1 - \frac{V_{X_{\sim i}}[E_{X_i}(Y|X_{\sim i})]}{V(Y)}$$

**اثر مرتبه دوم:**

$$S_{ij} = \frac{V_{X_{ij}}[E_{X_{\sim ij}}(Y|X_i,X_j)]}{V(Y)} - S_i - S_j$$

#### ۸.۴.۲. روش Morris (غربالگری اولیه)

$$d_i(\mathbf{x}) = \frac{f(x_1,...,x_i+\Delta,...,x_p) - f(\mathbf{x})}{\Delta}$$

$$\mu_i^* = \frac{1}{r}\sum_{j=1}^r |d_i(\mathbf{x}_j)|$$

$$\sigma_i = \sqrt{\frac{1}{r-1}\sum_{j=1}^r (d_i(\mathbf{x}_j) - \mu_i)^2}$$

---

## بخش نهم: نقشه راه توسعه علمی

### فاز ۱ (ماه ۱-۴): هسته محاسباتی فیزیکی-شیمیایی

**اهداف:**
- پیاده‌سازی حل‌گر FEM برای معادله ریچاردز با هیسترزیس و اثرات حرارتی
- توسعه موتور DayCent بومی با ۷ مخزن کربن
- ادغام داده‌های Sentinel-1/2 با الگوریتم‌های EWCM و PROSAIL
- کالیبراسیون با داده‌های میدانی اولیه

**خروجی‌ها:**
- کد Python/Rust برای حل PDEها
- کتابخانه PROSAIL بومی
- پایگاه داده پارامترهای خاک ایران

### فاز ۲ (ماه ۵-۸): هوش مصنوعی علمی و بهینه‌سازی

**اهداف:**
- آموزش PINNs برای جایگزینی حل‌گرهای عددی کند
- پیاده‌سازی EnKF برای Data Assimilation بلادرنگ
- توسعه QAOA-Inspired برای بهینه‌سازی توزیع آب
- استقرار PQC برای امنیت داده‌ها

**خروجی‌ها:**
- مدل‌های PINN آموزش‌دیده برای ۵ نوع خاک اصلی ایران
- سیستم بهینه‌سازی آب با کاهش ۲۰-۳۰% مصرف
- پروتکل‌های امنیتی پسا-کوانتومی

### فاز ۳ (ماه ۹-۱۲): یکپارچه‌سازی اقتصاد و جامعه

**اهداف:**
- پیاده‌سازی موتور ABM برای شبیه‌سازی رفتار کشاورزان
- اتصال موتور DayCent به قراردادهای هوشمند کربن
- توسعه شاخص قابلیت و تحلیل CGE
- اعتبارسنجی با داده‌های میدانی شرکت دشت امید نارون

**خروجی‌ها:**
- شبیه‌ساز رفتار جمعی ۱۰,۰۰۰ کشاورز مجازی
- سیستم توکنیزاسیون کربن
- داشبورد XAI برای کشاورزان

### فاز ۴ (ماه ۱۳-۱۸): اعتبارسنجی و مقیاس‌پذیری

**اهداف:**
- تحلیل عدم قطعیت جامع با PCE و مونت کارلو
- تست مقیاس‌پذیری برای ۱۰,۰۰۰+ مزرعه همزمان
- انتشار مقالات علمی و ثبت اختراع
- آماده‌سازی برای استقرار ملی

**خروجی‌ها:**
- گزارش اعتبارسنجی با معیارهای بین‌المللی
- مقاله در ژورنال‌های Q1
- پلتفرم آماده استقرار

---

## بخش دهم: چالش‌های علمی و افق‌های پژوهشی

### ۱۰.۱. چالش‌های باز

1. **عدم قطعیت ساختاری در مدل‌های خاک:**
   - راه‌حل: Bayesian Model Averaging (BMA)
   - $$P(M_k|D) = \frac{P(D|M_k)P(M_k)}{\sum_j P(D|M_j)P(M_j)}$$

2. **تلفیق مقیاس‌ها (Scale Bridging):**
   - راه‌حل: روش‌های Homogenization پیشرفته و Multiscale FEM

3. **مدل‌سازی برهم‌کنش ریشه-خاک:**
   - راه‌حل: استفاده از X-ray CT برای پارامترسازی دقیق

4. **پیش‌بینی Extreme Events:**
   - راه‌حل: Extreme Value Theory (EVT) و Copulas
   - $$F_{GPD}(x) = 1 - \left(1 + \xi\frac{x-\mu}{\sigma}\right)^{-1/\xi}$$

### ۱۰.۲. افق‌های نوآورانه

1. **Digital Twin با فیدبک بلادرنگ:**
   - استفاده از Reinforcement Learning برای کنترل بهینه آبیاری

2. **Foundation Models for Earth Science:**
   - آموزش مدل‌های بنیادی روی پتابایت داده ماهواره‌ای

3. **Quantum Machine Learning:**
   - استفاده از VQE برای بهینه‌سازی پارامترهای مدل

4. **Federated Physics:**
   - آموزش مدل‌های فیزیکی به صورت توزیع‌شده با حفظ حریم خصوصی

---

## نتیجه‌گیری

این برنامه جامع، چارچوب نظری و عملیاتی کامل برای توسعه پلتفرم **هیدروما نوژین** به عنوان یک سیستم چند-مقیاسی و چند-فیزیکی مبتنی بر اصول اولیه ارائه می‌دهد. تمامی معادلات و الگوریتم‌ها به گونه‌ای طراحی شده‌اند که:

1. **بدون وابستگی** به مدل‌های تجاری و با حفظ مالکیت فکری کامل
2. **قابل پیاده‌سازی** در مقیاس سیاره‌ای با منابع محاسباتی محدود
3. **قابل اعتبارسنجی** با معیارهای بین‌المللی علمی
4. **قابل توسعه** برای افزودن ماژول‌های جدید در آینده

این سند به عنوان مرجع علمی اصلی برای تیم توسعه پلتفرم اکو نوژین و مقاله‌های علمی آینده استفاده خواهد شد.