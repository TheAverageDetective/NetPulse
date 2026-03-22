"""
Call this python file with arguments

python main.py --url <download_url> --time <download_interval_minutes>


The code will create a thread to call the download function.
That thread will download, store data, then create a 

"""

def main():
    print("Network Traffic Analyzer")
    print("Hello from main module :D")

    import argparse

    # Obtain the cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=False, default="https://stpes2ug24cs784388567931.file.core.windows.net/6c48981d-f8aa-4fb3-b21c-d5d503f50a55-code/peppa1.mp4?sp=r&st=2026-03-22T15:29:34Z&se=2026-04-30T15:45:00Z&sv=2024-11-04&sig=jn47d8f4kmtWLC5P4MdoE8WFRrN7dDbPnqy3eH4jAN0%3D&sr=f")
    parser.add_argument("--time", type=int, required=False, default=1)
    args = parser.parse_args()

    download_url = args.url
    download_interval_minutes = args.time
    print(download_url, download_interval_minutes)



    # TODO: Call the download function with download_url here.



if __name__ == '__main__':
    main()