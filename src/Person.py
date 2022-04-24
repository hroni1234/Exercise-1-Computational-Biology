class Person:
    def __init__(self, GENERATIONS_TO_RECOVERY=3,is_fast=False,is_covid=False,is_healed=False,days_to_recovery=0):
        self.is_fast = is_fast
        self.is_covid = is_covid
        self.is_healed=is_healed
        self.days_to_recovery=days_to_recovery
        # self.steps_from_prev_pos_x = 0
        # self.steps_from_prev_pos_y=0
        self.generations_to_recovery=GENERATIONS_TO_RECOVERY

    # def move(self, step_x, step_y):
    #     self.steps_from_prev_pos_x = step_x
    #     self.steps_from_prev_pos_y = step_y


    def infected(self,):
        if not self.is_healed and not self.is_covid:
            self.is_covid=True
            self.days_to_recovery=self.generations_to_recovery

    def healed(self):
        if self.days_to_recovery==0 and self.is_covid:
            self.is_covid=False
            self.is_healed=True

    def generation_passed(self):
        if self.is_covid:
            self.days_to_recovery-=1
            if self.days_to_recovery==0:
                self.healed()
