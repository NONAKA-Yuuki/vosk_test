#!/usr/bin/python
import queue
import sys
import time
import re
import json
import logging
import sounddevice as sd

from vosk import Model, KaldiRecognizer

#================ logging設定 ==================
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s %(name)s %(levelname)s] %(message)s")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)
#===============================================

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# parser = argparse.ArgumentParser(add_help=False)
# parser.add_argument(
#     "-l", "--list-devices", action="store_true",
#     help="show list of audio devices and exit")
# args, remaining = parser.parse_known_args()
# if args.list_devices:
#     print(sd.query_devices())
#     parser.exit(0)
# parser = argparse.ArgumentParser(
#     description=__doc__,
#     formatter_class=argparse.RawDescriptionHelpFormatter,
#     parents=[parser])
# parser.add_argument(
#     "-f", "--filename", type=str, metavar="FILENAME",
#     help="audio file to store recording to")
# parser.add_argument(
#     "-d", "--device", type=int_or_str,
#     help="input device (numeric ID or substring)")
# parser.add_argument(
#     "-r", "--samplerate", type=int, help="sampling rate")
# parser.add_argument(
#     "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
# args = parser.parse_args(remaining)

def preprocess(text):
    # 空白を消す
    text = re.sub(r"\s", "", text)
    return text


# config model
device = None
device_info = sd.query_devices(device, "input")
samplerate = int(device_info["default_samplerate"])
# model = Model(lang = "ja")
# ./modelからload
model = Model("model")

def recognize():
    recognized_text = ""
    
    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=device,
                            dtype="int16", channels=1, callback=callback):
        # print("#" * 80)
        # print("Press Ctrl+C to stop the recording")
        # print("#" * 80)

        count = 0
        start_time = time.time()
        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                # parse json
                text = json.loads(result)["text"]
                if len(text) > 0 :
                    text = preprocess(text)
                    recognized_text = text # 最終出力
                    logger.info(f"Recognized text: {text}")
                    logger.debug("break")
                    break

            else:
                partial = json.loads(rec.PartialResult())["partial"]
                if len(partial) == 0:
                    count += 1
                else:
                    count = 0 # reset
            
            if count > 20: # count *  1/fs * blocksize = timeout
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.debug(f"elapsed time: {elapsed_time}")
                logger.info("timeout")
                break
    
    logger.debug(f"count: {count}")
    return recognized_text


if __name__ == '__main__':
    text = recognize()
    print(text)