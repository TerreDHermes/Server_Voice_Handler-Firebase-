import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import os
import time



def move_audio(bucket, root_folder):
    # Определите пути к папкам "audio" и "text" для текущей корневой папки
    audio_folder = root_folder + '/audio/'
    text_folder = root_folder + '/text/'
    base_file_path = '/base/base.txt'
    base_folder = '/base/'
    text_base_file_path = os.path.join(base_folder, 'text_base.txt')

    if not os.path.exists('/base/' + root_folder + '/audio/'):
        os.makedirs('/base/' + root_folder + '/audio/')

    if not os.path.exists('/base/' + root_folder + '/text/'):
        os.makedirs('/base/' + root_folder + '/text/')

    if not os.path.exists(base_file_path):
        open(base_file_path, 'w').close()  # Создаем файл, если он не существует

    if not os.path.exists(text_base_file_path):
        open(text_base_file_path, 'w').close()  # Создаем файл, если он не существует

    # Читаем содержимое файла base.txt для получения списка обработанных файлов
    with open(base_file_path, 'r') as base_file:
        processed_files = set(base_file.read().splitlines())



    # Читаем содержимое файла text_base.txt для получения списка уже отправленных файлов
    with open(text_base_file_path, 'r') as text_base_file:
        sent_files = set(text_base_file.read().splitlines())

    # Получите список всех объектов в папке "audio" текущей корневой папки
    audio_objects = bucket.list_blobs(prefix=audio_folder)

    # Переносим каждый объект из папки "audio" в папку "text"
    for audio_object in audio_objects:
        if audio_object.name.lower().endswith('.3gp') and audio_object.name not in processed_files:
            file_name = os.path.basename(audio_object.name)
            print(audio_object.name, file_name)
            audio_object.download_to_filename(os.path.join('/base/', root_folder, 'audio', file_name))
            processed_files.add(audio_object.name)

            # Записываем обновленный список обработанных файлов в файл base.txt
            with open(base_file_path, 'w') as base_file:
                base_file.write('\n'.join(processed_files))

    for file_name in os.listdir('/base/' + root_folder + '/text/'):
        if os.path.isfile('/base/' + root_folder + '/text/' + file_name) and os.path.join(base_folder, root_folder, 'text', file_name) not in sent_files:
            blob_name = text_folder + file_name
            blob = bucket.blob(blob_name)
            blob.upload_from_filename('/base/' + root_folder + '/text/' + file_name)
            if (file_name != 'ALL_TEXT.pdf' and file_name != 'ALL_TEXT.txt'):
                sent_files.add(os.path.join(base_folder, root_folder, 'text', file_name))
                with open(text_base_file_path, 'w') as text_base_file:
                    text_base_file.write('\n'.join(sent_files))



def create_audio_text_folders(bucket, root_folder):
    # Проверяем наличие папок "audio" и "text" в текущей корневой папке
    audio_folder = root_folder + '/audio/'
    text_folder = root_folder + '/text/'

    if not bucket.get_blob(audio_folder):
        # Если папки "audio" нет, создаем ее
        bucket.blob(audio_folder).upload_from_string('')

    if not bucket.get_blob(text_folder):
        # Если папки "text" нет, создаем ее
        bucket.blob(text_folder).upload_from_string('')


def main():
    cred = credentials.Certificate("C:/Users/vikde/PycharmProjects/Server_Voice_Handler/voice-app-8f616-firebase-adminsdk-ypcs1-b680e9ccc9.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'voice-app-8f616.appspot.com'
    })

    bucket = storage.bucket()

    while(True):
        # Получите список всех корневых папок
        root_folders = set()
        all_objects = bucket.list_blobs()
        for object in all_objects:
            parts = object.name.split('/')
            if len(parts) >= 2:
                root_folder = parts[0]
                root_folders.add(root_folder)

        # Переберите каждую корневую папку и создайте папки "audio" и "text" при необходимости
        for root_folder in root_folders:
            create_audio_text_folders(bucket, root_folder)

        for root_folder in root_folders:
            move_audio(bucket, root_folder)

        time.sleep(6)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
        main()


