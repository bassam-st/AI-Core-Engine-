class AutoTrainer:
    def __init__(self, intent_model, memory):
        self.intent_model = intent_model
        self.memory = memory

    def maybe_learn(self, text, intent):
        # مسك مكان — يمكنك لاحقًا انتقاء محادثات ناجحة وإضافتها كأمثلة
        pass

    def learn_from_memory(self) -> int:
        # حالياً: نعيد تدريب المصنف إذا أضفت أمثلة يدويًا عبر /train/manual
        self.intent_model.train()
        return 0
