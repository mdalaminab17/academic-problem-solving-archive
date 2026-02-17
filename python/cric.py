import json
import base64
import urllib.request
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import os
from colorama import Fore, Style, init as colorama_init
from tqdm import tqdm
colorama_init(autoreset=True)

## --- Algoritmo de Decodificación Descubierto ---

# Replicando el bloque estático del código Java
plain = ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F', 'g', 'G', 'h', 'H', 'i', 'I', 'j', 'J', 'k', 'K', 'l', 'L', 'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', 'q', 'Q', 'r', 'R', 's', 'S', 't', 'T', 'u', 'U', 'v', 'V', 'w', 'W', 'x', 'X', 'y', 'Y', 'z', 'Z']
cipher = ['f', 'F', 'g', 'G', 'j', 'J', 'k', 'K', 'a', 'A', 'p', 'P', 'b', 'B', 'm', 'M', 'o', 'O', 'z', 'Z', 'e', 'E', 'n', 'N', 'c', 'C', 'd', 'D', 'r', 'R', 'q', 'Q', 't', 'T', 'v', 'V', 'u', 'U', 'x', 'X', 'h', 'H', 'i', 'I', 'w', 'W', 'y', 'Y', 'l', 'L', 's', 'S']

# Crear el diccionario de mapeo inverso
reverse_map = {ord(c): p for p, c in zip(plain, cipher)}

def decode_string(s):
    """Decodifica una cadena usando el cifrado de sustitución inverso y Base64."""
    try:
        s = s.replace('\\', '').replace('\n', '') # Eliminar barras y saltos de línea
        substituted_chars = []
        for char in s:
            char_ord = ord(char)
            if char_ord in reverse_map:
                substituted_chars.append(reverse_map[char_ord])
            else:
                substituted_chars.append(char)
        
        substituted_string = "".join(substituted_chars)
        decoded_bytes = base64.b64decode(substituted_string)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return f"DECODING_ERROR: {s}" # Devolver un error claro si falla

# --- Lógica Principal del Script ---

def fetch_url(url, timeout=15, retries=3, delay=2):
    """Obtiene el contenido de una URL con caché, timeout y reintentos."""
    if not hasattr(fetch_url, "cache"):
        fetch_url.cache = {}
        fetch_url.lock = threading.Lock()
    with fetch_url.lock:
        if url in fetch_url.cache:
            return fetch_url.cache[url]
    last_exception = None
    for attempt in range(retries):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
                result = response.read().decode('utf-8')
                with fetch_url.lock:
                    fetch_url.cache[url] = result
                return result
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"{Fore.RED}❌  404 Not Found: {url}{Style.RESET_ALL}")
                with fetch_url.lock:
                    fetch_url.cache[url] = None
                return None
            print(f"{Fore.RED}❌  Error fetching {url} (attempt {attempt+1}/{retries}): {e}{Style.RESET_ALL}")
            time.sleep(delay)
        except urllib.error.URLError as e:
            print(f"{Fore.RED}❌  Connection error fetching {url}: {e}{Style.RESET_ALL}")
            with fetch_url.lock:
                fetch_url.cache[url] = None
            return None
        except Exception as e:
            print(f"{Fore.RED}❌  Error fetching {url} (attempt {attempt+1}/{retries}): {e}{Style.RESET_ALL}")
            time.sleep(delay)
    with fetch_url.lock:
        fetch_url.cache[url] = None
    return None



# --- Procesamiento paralelo de enlaces ---
def build_full_link_url(link_path, base_url):
    path_parts = link_path.split('/')
    if len(path_parts) > 1:
        encoded_filename = urllib.parse.quote(path_parts[-1])
        return base_url + "/".join(path_parts[:-1]) + "/" + encoded_filename
    else:
        return base_url + urllib.parse.quote(link_path)

def process_single_link(link_path, base_url):
    full_link_url = build_full_link_url(link_path, base_url)
    links_json_str = fetch_url(full_link_url)
    if links_json_str:
        try:
            links_data = json.loads(links_json_str)
            if 'links' in links_data and isinstance(links_data['links'], str):
                final_links_encoded = links_data['links']
                final_links_decoded_str = decode_string(final_links_encoded)
                try:
                    result = json.loads(final_links_decoded_str)
                    return result
                except json.JSONDecodeError:
                    return {"error": "La cadena final de links no es un JSON válido", "decoded_text": final_links_decoded_str}
            else:
                return links_data
        except Exception as e:
            return {"error": f"Error procesando el JSON de links: {e}"}
    else:
        return {"error": f"No se pudo obtener el fichero de enlaces. Último error: {fetch_url.cache.get(full_link_url, 'desconocido')}"}

def find_links(obj, base_url, links_to_process):
    """Recorre el objeto y acumula referencias a campos 'links' para procesar en paralelo."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'links' and isinstance(v, str):
                links_to_process.append((obj, k, v))
            else:
                find_links(v, base_url, links_to_process)
    elif isinstance(obj, list):
        for item in obj:
            find_links(item, base_url, links_to_process)
    # Si es otro tipo, no hace nada

def parse_m3u(m3u_content, max_channels=10, save_dir="m3u_files"):
    """Convierte contenido M3U en una lista de canales y guarda el archivo si es muy largo."""
    if not m3u_content or not isinstance(m3u_content, str):
        return {"error": "Contenido M3U vacío o inválido."}
    lines = [line.strip() for line in m3u_content.splitlines() if line.strip()]
    channels = []
    current_channel = {}
    for line in lines:
        if line.startswith("#EXTINF"):
            current_channel = {"info": line}
        elif line.startswith("http"):
            if current_channel:
                current_channel["url"] = line
                channels.append(current_channel)
                current_channel = {}

    else:
        return {"channels": channels}


def clean_escapes(obj):
    """Recursively remove escape slashes from URLs and embedded JSON strings."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Clean URLs
            if isinstance(v, str) and (v.startswith('http') or v.startswith('https')):
                obj[k] = v.replace('\\/', '/').replace('\\', '')
            # Clean embedded JSON
            elif isinstance(v, str) and v.startswith('{') and v.endswith('}'):
                try:
                    parsed = json.loads(v.replace('\\/', '/').replace('\\', ''))
                    obj[k] = clean_escapes(parsed)
                except Exception:
                    obj[k] = v.replace('\\/', '/').replace('\\', '')
            else:
                obj[k] = clean_escapes(v)
        return obj
    elif isinstance(obj, list):
        return [clean_escapes(item) for item in obj]
    elif isinstance(obj, str):
        return obj.replace('\\/', '/').replace('\\', '')
    else:
        return obj

def main():
    """Función principal para ejecutar todo el proceso."""
    base_url = "https://mkvcinemas.co/"
    api_path = "app.json"
    final_output_filename = "app_links.json"
    
    print(f"{Fore.CYAN}🔎  Step 1: Fetching main configuration from {base_url}{api_path}...{Style.RESET_ALL}")
    main_config_str = fetch_url(base_url + api_path)
    if not main_config_str:
        print(f"{Fore.RED}❌  Could not fetch main configuration!{Style.RESET_ALL}")
        return
    encoded_data_list = json.loads(main_config_str)

    print(f"{Fore.GREEN}✅  Step 2: Main configuration fetched. Decoding all layers...{Style.RESET_ALL}")
    fully_decoded_data = []

    for item_dict in tqdm(encoded_data_list, desc=f"{Fore.YELLOW}Decoding items", colour="yellow"):
        decoded_item = item_dict.copy()

        # --- PROCESS 'events' SECTION ---
        if 'events' in decoded_item and isinstance(decoded_item['events'], str):
            print(f"{Fore.BLUE}   📅  Processing 'events' section...{Style.RESET_ALL}")
            try:
                encoded_list = json.loads(decoded_item['events'])
                decoded_events = []
                for encoded_item_str in encoded_list:
                    decoded_event_str = decode_string(encoded_item_str)
                    try:
                        event_obj = json.loads(decoded_event_str)
                        decoded_events.append(event_obj)
                    except json.JSONDecodeError:
                        decoded_events.append({"error": "Could not parse decoded event", "original": decoded_event_str})
                decoded_item['events'] = decoded_events
            except (json.JSONDecodeError, TypeError): pass

        # --- PROCESS 'categories' SECTION ---
        if 'categories' in decoded_item and isinstance(decoded_item['categories'], str):
            print(f"{Fore.BLUE}   🗂️  Processing 'categories' section...{Style.RESET_ALL}")
            try:
                encoded_list = json.loads(decoded_item['categories'])
                decoded_categories = []
                for encoded_item_str in encoded_list:
                    decoded_item_json_str = decode_string(encoded_item_str)
                    try:
                        cat_obj = json.loads(decoded_item_json_str)
                        if cat_obj.get('type') == 'm3u':
                            m3u_url = cat_obj.get('api')
                            if m3u_url:
                                print(f"{Fore.MAGENTA}     📺  Fetching M3U content for '{cat_obj.get('name')}'...{Style.RESET_ALL}")
                                m3u_content = fetch_url(m3u_url)
                                cat_obj['api'] = parse_m3u(m3u_content) if m3u_content else {"error": f"Could not fetch M3U content. Last error: {fetch_url.cache.get(m3u_url, 'unknown')}"}
                        elif cat_obj.get('type') == 'custom':
                            link_path = cat_obj.get('api')
                            if link_path:
                                full_link_url = base_url + link_path
                                print(f"{Fore.MAGENTA}     🧩  Fetching CUSTOM sub-channels for '{cat_obj.get('name')}'...{Style.RESET_ALL}")
                                sub_channels_str = fetch_url(full_link_url)
                                if sub_channels_str:
                                    try:
                                        sub_channels_list = json.loads(sub_channels_str)
                                        processed_sub_channels = []
                                        if isinstance(sub_channels_list, list):
                                            for sub_channel in sub_channels_list:
                                                if 'channel' in sub_channel and isinstance(sub_channel['channel'], str):
                                                    decoded_channel_str = decode_string(sub_channel['channel'])
                                                    try:
                                                        final_channel_obj = json.loads(decoded_channel_str)
                                                        processed_sub_channels.append(final_channel_obj)
                                                    except json.JSONDecodeError:
                                                        processed_sub_channels.append({"error": "Final channel string is not valid JSON", "decoded_text": decoded_channel_str})
                                                else:
                                                    processed_sub_channels.append(sub_channel)
                                        cat_obj['api'] = processed_sub_channels
                                    except Exception as e:
                                        cat_obj['api'] = {"error": f"Error processing sub-channels list: {e}"}
                                else:
                                    cat_obj['api'] = {"error": f"Could not fetch sub-channels file. Last error: {fetch_url.cache.get(full_link_url, 'unknown')}"}
                        decoded_categories.append(cat_obj)
                    except json.JSONDecodeError:
                        decoded_categories.append({"error": "Could not parse decoded category", "original": decoded_item_json_str})
                decoded_item['categories'] = decoded_categories
            except (json.JSONDecodeError, TypeError): pass

        decoded_item = clean_escapes(decoded_item)
        fully_decoded_data.append(decoded_item)

    # --- Process all 'links' in parallel ---
    print(f"{Fore.CYAN}🚀  Processing all 'links' in parallel...{Style.RESET_ALL}")
    links_to_process = []
    for item in fully_decoded_data:
        find_links(item, base_url, links_to_process)

    # Parallel processing with progress bar
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(process_single_link, link_path, base_url) for obj, k, link_path in links_to_process]
        for i, future in enumerate(tqdm(futures, desc=f"{Fore.YELLOW}Processing links", colour="yellow")):
            obj, k, _ = links_to_process[i]
            try:
                obj[k] = clean_escapes(future.result())
            except Exception as e:
                obj[k] = {"error": f"Parallel processing error: {e}"}

    print(f"{Fore.GREEN}✅  Step 3: Decoding completed and links processed in parallel.{Style.RESET_ALL}")

    try:
        with open(final_output_filename, 'w', encoding='utf-8') as f:
            json.dump(fully_decoded_data, f, ensure_ascii=False, indent=4)
        print(f"{Fore.GREEN}🎉  Success! The final and complete report has been saved to '{final_output_filename}'{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌  Error: Could not write output file. {e}{Style.RESET_ALL}")

if __name__ == '__main__':
    main()