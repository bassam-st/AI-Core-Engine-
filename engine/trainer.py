from .memory import ConversationMemory
from .intent import IntentModel

class AutoTrainer:
    def __init__(self, intent: IntentModel, memory: ConversationMemory):
        self.intent = intent
        self.memory = memory
        self.counter = 0

    def maybe_learn(self, text: str, label: str):
        # تدريب بسيط كل 25 رسالة
        self.intent.add_examples([(text, label)])
        self.counter += 1
        if self.counter % 25 == 0:
            self.intent.train()

    def learn_from_memory(self) -> int:
        rows = self.memory.all(limit=500)
        pairs = [(msg, intent) for (_, msg, _, intent, _, _) in rows if msg and intent]
        for p in pairs:
            self.intent.add_examples([p])
        if pairs:
            self.intent.train()
        return len(pairs)
