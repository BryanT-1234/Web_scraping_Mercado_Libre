from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Configuración del servicio para Edge WebDriver
service = Service("msedgedriver.exe")  # Cambiar la ruta si es necesario del driver del navegador(Microsoft Edge en este caso)
driver = webdriver.Edge()

# URL base de "zapatillas futbol" de Mercado Libre
url_base = "https://listado.mercadolibre.com.pe/ropa-accesorios/calzado/zapatillas/zapatillas-futbol{}NoIndex_True"

# Variables de control
# establecidas por la forma del url de mercado libre
primera_vez = True
num_identado = 49
productos = []

try:
    while True:
        # Construir URL
        if primera_vez:
            # Para el primer URL _NoIndex
            url_pagina = url_base.format("_")
            primera_vez = False
        else:
            # Para los demás URL : _Desde_49_ , _Desde_97_ , .....
            url_pagina = url_base.format(f"_Desde_{num_identado}_")
            num_identado += 48

        # Navegar a la página
        driver.get(url_pagina)

        # Esperar a que las tarjetas de producto estén presentes
        try:
            tarjetas = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".poly-card__content"))
            )
        except Exception as e:
            # Se rompe el ciclo de busqueda al no haber mas productos
            print(f"No se encontraron productos en la página: {url_pagina}")
            break

        # Procesar cada tarjeta
        for tarjeta in tarjetas:
            try:
                # Extraer marca (si existe)
                try:
                    marca_elemento = tarjeta.find_element(By.CSS_SELECTOR, "span.poly-component__brand")
                    marca = marca_elemento.text
                except:
                    marca = "N/A"

                # Extraer nombre del producto 
                try:
                    nombre_elemento = tarjeta.find_element(By.CSS_SELECTOR, "h2.poly-box.poly-component__title a")
                    nombre = nombre_elemento.text
                except:
                    nombre = "N/A"

                # Extraer precio
                try:
                    # Obtener la parte entera y limpiar puntos de miles para casos como S/1.100 mil soles
                    precio_entero = tarjeta.find_element(By.CSS_SELECTOR, "span.andes-money-amount__fraction").text
                    precio_entero = precio_entero.replace(".", "")  # Eliminar separadores de miles
                    
                    # Obtener los centavos
                    try:
                        precio_decimales = tarjeta.find_element(By.CSS_SELECTOR, "span.andes-money-amount__cents").text
                        precio = f"{precio_entero}.{precio_decimales}"  # Concatenar entero y centimos
                    except:
                        precio = precio_entero  # Si no hay centimos, usar solo la parte entera
                except:
                    precio = "N/A"

                # Agregar datos del producto a la lista
                productos.append({
                    "Marca": marca,
                    "Nombre": nombre,
                    "Precio": precio
                })
            except Exception as e:
                print(f"Error al procesar una tarjeta: {e}")

        print(f"Página procesada: {url_pagina}")

except Exception as e:
    print(f"Error durante el scraping: {e}")
finally:
    # Cerrar el navegador
    driver.quit()

# Convertir los datos a DataFrame con pandas
df = pd.DataFrame(productos)

# Guardar los datos en un archivo CSV para su posterior uso
df.to_csv("productos_scraped.csv", index=False)

print("Scraping completado. Datos guardados en 'productos_scraped.csv'.")
