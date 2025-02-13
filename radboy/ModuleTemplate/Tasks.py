from radboy.DB.db import *
class TasksMode:
    def __init__(self,engine):
        self.engine=engine
        self.options={
                '1':{
                    'cmds':['q','quit','1'],
                    'desc':"quit program",
                    'exec':lambda: exit("user quit!"),
                    },
                '2':{
                    'cmds':['b','back','2'],
                    'desc':'go back menu if any',
                    'exec':None
                    },
                }
        while True:
            for option in self.options:
                print(f"{self.options[option]['cmds']} - {self.options[option]['desc']}")
            command=input("do what: ")
            for option in self.options:
                if self.options[option]['exec'] != None and command.lower() in self.options[option]['cmds']:
                    self.options[option]['exec']()
                elif self.options[option]['exec'] == None and command.lower() in self.options[option]['cmds']:
                    return


if __name__ == "__main__":
    TasksMode(engine=ENGINE)
