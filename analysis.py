import math

def get_permittivites(core_radius, radius,
                      medium_permittivity,
                      core_permittivity):
    beta = (core_radius/radius)**3
    x = 2* (1 + beta) / (2 * beta + 1)
    y = 4*(1-beta)/(2*beta+1)
    t = core_permittivity/medium_permittivity
    e_1p = ((-medium_permittivity/y)*
            ((t+x)+((t+x)**2-y**2*t)**(1/2)))
    e_2p = ((-medium_permittivity / y) *
            ((t + x) - ((t + x) ** 2 - y ** 2 * t) ** (1 / 2)))
    e_1t = ((-medium_permittivity / y) *
            ((t - x/2) + ((t - x/2) ** 2 + y ** 2 * t/2) ** (1 / 2)))
    e_2t = ((-medium_permittivity / y) *
            ((t - x / 2) - ((t - x / 2) ** 2 + y ** 2 * t / 2) ** (1 / 2)))
    return([e_1p, e_2p, e_1t, e_2t])

def get_wavelength(permittivity, inf_permittivity,
                   gamma, plasm_frequency):
    wave_speed = 3*10**8
    h = 6.58*10**(-16)
    f = 10**(-15)
    omega = math.sqrt((plasm_frequency/h)**2/
                      (inf_permittivity-permittivity)-(gamma/f)**2)
    wavelength = (2*math.pi*wave_speed)*10**(9)/omega
    return(wavelength)
