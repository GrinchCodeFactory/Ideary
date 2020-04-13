import datetime


class DiaryEntry:

    def __init__(self, number: int, text: str, timestamp: datetime.datetime, diary_id, _id=None, tagList: [] = [],
                 image: str = ''):
        self.number = number
        self.text = text
        self.timestamp = timestamp
        self.diary_id = diary_id
        self.tagList = tagList
        self.image = image

    def __str__(self):
        return f"#{self.number}: {self.text} @{self.timestamp} (D{self.diary_id})"


class Diary:

    def __init__(self, diary_id, user_id):
        self.diary_id = diary_id
        self.user_id = user_id

    def add_entry(self, entry: DiaryEntry) -> DiaryEntry:
        import src.ideary.storage as storage
        entry = storage.write_entry(entry, diary_id=self.diary_id)
        return entry

    def next_entry_number(self):
        import src.ideary.storage as storage
        entry = storage.get_latest_entry(self.diary_id)
        return (entry.number + 1) if entry else 1

    def get_entry(self, number):
        import src.ideary.storage as storage
        return storage.read_entry(diary_id=self.diary_id, number=number)


if __name__ == '__main__':
    diary = Diary(diary_id=0, user_id=0)
    entry = DiaryEntry(number=diary.next_entry_number(), text='test', timestamp=datetime.datetime.now(),
                       diary_id=diary.diary_id)
    print('new entry', entry)
    diary.add_entry(entry=entry)

    got = diary.get_entry(1)
    print('got', got)
