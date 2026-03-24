"""
Call this python file with arguments

python main.py --url <download_url> --time <download_interval_minutes>
Other options: --file <filepath> --report <reportpath> --chart <chartpath>
"""

def main():
    import argparse, os
    from src import dl_thread, analysis, charts

    # Obtain the cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=False, default="https://stpes2ug24cs784388567931.file.core.windows.net/6c48981d-f8aa-4fb3-b21c-d5d503f50a55-code/peppa1.mp4?sp=r&st=2026-03-22T15:29:34Z&se=2026-04-30T15:45:00Z&sv=2024-11-04&sig=jn47d8f4kmtWLC5P4MdoE8WFRrN7dDbPnqy3eH4jAN0%3D&sr=f")
    parser.add_argument("--time", type=int, required=False, default=1)
    parser.add_argument("--file", type=str, required=False, default="data/data.csv")
    parser.add_argument("--report", type=str, required=False, default="data/report.json")
    parser.add_argument("--chart", type=str, required=False, default="data/chart.jpg")
    args = parser.parse_args()

    download_url : str = args.url
    download_interval_minutes : int = args.time
    filepath : str = os.path.abspath(args.file)
    reportpath : str = os.path.abspath(args.report)
    chartpath : str = os.path.abspath(args.chart)


    # Run the thread that will do the download
    print("\nNetwork Traffic Analyzer :D")
    print("Enter 'q' at any time to stop\n")

    dl_thread.start(download_url, download_interval_minutes, filepath)
    input()
    dl_thread.stop()


    # Perform statistics and generate chart here
    analysis.analyze(filepath, reportpath)
    charts.generate(filepath, chartpath)



if __name__ == '__main__':
    main()
