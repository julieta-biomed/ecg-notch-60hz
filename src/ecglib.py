import numpy as np
from scipy import signal as sg

def ecg_sintetico(fs=500, dur=20.0, hr=62.0, amp_r=1.30, hrv=0.045, semilla=7):
    """ECG sintético por suma de gaussianas, con variabilidad natural del RR.

    hrv: desviación estándar del intervalo RR en segundos (0 = ritmo perfecto).
         Un valor de ~0.045 s produce una variabilidad fisiológicamente plausible
         y evita el peine espectral artificial de una señal exactamente periódica.
    """
    rng = np.random.default_rng(semilla)
    n = int(fs*dur); t = np.arange(n)/fs; x = np.zeros(n)
    ondas = [(-0.200, 0.15, 0.025), (-0.035,-0.10, 0.008), (0.0, 1.10, 0.010),
             ( 0.035,-0.25, 0.010), ( 0.280, 0.30, 0.045)]
    rr_medio = 60.0/hr
    tr = 0.4; picos = []
    while tr < dur - 0.5:
        picos.append(tr)
        for c,a,s in ondas:
            x += a*np.exp(-0.5*((t-(tr+c))/s)**2)
        tr += max(0.35, rng.normal(rr_medio, hrv))
    return t, x*(amp_r/1.10), np.array(picos)

def deriva(t, amp=0.35, f_resp=0.28):
    """Deriva de línea base: respiración (~17 resp/min) y movimiento de electrodos."""
    return (amp*np.sin(2*np.pi*f_resp*t) + 0.18*np.sin(2*np.pi*0.09*t+1.1)
            + 0.08*np.sin(2*np.pi*0.55*t+2.3))

def red(t, amp=0.12, f0=60.0):
    """Interferencia de red: fundamental y armónicos por acoplo capacitivo."""
    return (amp*np.sin(2*np.pi*f0*t) + 0.28*amp*np.sin(2*np.pi*2*f0*t+0.7)
            + 0.16*amp*np.sin(2*np.pi*3*f0*t+1.9))

def emg(t, fs, amp=0.05, semilla=11):
    """Artefacto EMG: ruido de banda 20-150 Hz, en ráfagas."""
    rng = np.random.default_rng(semilla)
    sos = sg.butter(4, [20,150], 'bandpass', fs=fs, output='sos')
    ruido = sg.sosfilt(sos, rng.standard_normal(len(t)))
    env = 1 + 2.2*np.exp(-0.5*((t-8.2)/0.55)**2) + 1.8*np.exp(-0.5*((t-15.1)/0.4)**2)
    return amp*ruido*env
