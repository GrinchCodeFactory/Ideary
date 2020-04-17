import datetime
from typing import List


class Storabale:
    def __init__(self):
        self._known_fields = set(self.__dict__.keys())

    def __setattr__(self, key, value):
        if hasattr(self, '_known_fields') and key not in self._known_fields:
            raise TypeError('cannot set unknown field `%s`' % key)
        return super().__setattr__(key, value)

    def storage_state(self):
        d = self.__dict__.copy()
        del d['_known_fields']
        return d


class DiaryEntry(Storabale):
    def __init__(self, number: int, text: str, timestamp: datetime.datetime, diary_id, _id=None,
                 tag_list: List[str] = None,
                 image: str = ''):
        if tag_list is None:
            tag_list = []
        self.number = number
        self.text = text
        self.timestamp = timestamp
        self.diary_id = diary_id
        self.tag_list = tag_list
        self.image = image
        super().__init__()

    def __str__(self):
        return f"#{self.number}: {self.text} @{self.timestamp} (D{self.diary_id})"


class Diary:

    def __init__(self, diary_id, user_id):
        self.diary_id = int(diary_id)
        self.user_id = int(user_id)

    def add_entry(self, entry: DiaryEntry) -> DiaryEntry:
        import src.ideary.storage as storage
        entry = storage.write_entry(entry, diary_id=self.diary_id)
        return entry

    def next_entry_number(self):
        import src.ideary.storage as storage
        entry = storage.get_latest_entry(self.diary_id)
        return (entry.number + 1) if entry else 1

    def get_entry(self, number: int) -> DiaryEntry:
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
