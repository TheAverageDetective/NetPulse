"""
Call this python file with arguments

python main.py --url <download_url> --time <download_interval_minutes> --file <filepath>
"""

def main():
    import argparse, os
    from src import dl_thread, charts

    # Obtain the cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=False, default="https://stpes2ug24cs784388567931.file.core.windows.net/6c48981d-f8aa-4fb3-b21c-d5d503f50a55-code/peppa1.mp4?sp=r&st=2026-03-22T15:29:34Z&se=2026-04-30T15:45:00Z&sv=2024-11-04&sig=jn47d8f4kmtWLC5P4MdoE8WFRrN7dDbPnqy3eH4jAN0%3D&sr=f")
    parser.add_argument("--time", type=int, required=False, default=1)
    parser.add_argument("--file", type=str, required=False, default="data/data.csv")
    parser.add_argument("--chart", type=str, required=False, default="data/chart.jpg")
    args = parser.parse_args()

    download_url : str = args.url
    download_interval_minutes : int = args.time
    filepath : str = os.path.abspath(args.file)
    chartpath : str = os.path.abspath(args.chart)
    if not os.path.exists(filepath) : return print("Invalid file path, try again.")
    if not os.path.exists(chartpath) : return print("Invalid chart path, try again.")
    # print(download_url, download_interval_minutes, filepath, chartpath)

    print("Network Traffic Analyzer")
    print("Hello from main module :D")


    # Run the thread that will do the download
    dl_thread.start(download_url, download_interval_minutes, filepath)
    input("Enter 'q' at any time to stop\n")
    dl_thread.stop()


    # TODO: Perform statistics and generate chart here
    charts.generate(filepath, chartpath)



if __name__ == '__main__':
    main()