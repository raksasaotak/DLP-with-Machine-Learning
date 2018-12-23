from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser
import time

parser = configparser.ConfigParser()

class Watcher:
    ##TODO directorynya dari inputan user
    DIRECTORY_TO_WATCH = ''

    def __init__(self):
        self.observer = Observer()

    def watch_dir(self, what_dir):
        self.DIRECTORY_TO_WATCH = what_dir

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print ("Error")

        self.observer.join()

class Handler(FileSystemEventHandler):

    ##Untuk sekarang cuma kalo file di buat, di modify, atau di move baru watchernya logging. Gunanya watcher untuk kalo ada file baru atau yg di edit bakal di extract textnya buat di cek confidential atau enggak
    @staticmethod
    def on_any_event(event):
        new_file = []
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print ("Received created event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt','a')
            changelog.write('created, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print ("Received modified event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt', 'a')
            changelog.write('modified, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

        elif event.event_type == 'moved':
            # Taken any action here when a file is moved.
            print ("Received moved event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt', 'a')
            changelog.write('moved, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

        # elif event.event_type == 'deleted':
        #     # Taken any action here when a file is deleted.
        #     print ("Received deleted event - %s." % event.src_path)
        #     new_file.append(event.src_path.split('/')[-1:])
        #     changelog = open('clog.txt', 'a')
        #     changelog.write('deleted, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
        #     changelog.close()

if __name__ == '__main__':
        conf_File = 'testong.ini'
        parser.read(conf_File)
        w = Watcher()
        w.watch_dir(parser.get('folder_protect', 'folder')) #Ganti directorynya disini
        w.run()
