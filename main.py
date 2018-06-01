from tkinter import StringVar
from typing import Tuple
from fuzzywuzzy import fuzz
from rake.rake import Rake
from heapq import nlargest
from operator import itemgetter
from nltk.corpus import wordnet
from tkinter import *
from tkinter.ttk import *
import math


def check_synonyms(QW, keywords: tuple, p, q):
    max_fuzz_score = p
    key_word_score = q
    key_word_max = ""
    if " " in QW:
        qw: list = QW.split(" ")
    else:
        qw: list = [QW]

    for word in qw:
        synonyms = []
        #print("checking the synonyms of " + word)
        #print(keywords)
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        if synonyms is not None:
            for qws in synonyms:  # taking each of the question words
                for KW in keywords:  # taking each
                    kw = KW.split(',')
                    y = get_fuzz_score(kw[0], qws)  # calculating the the match between words
                    if y > max_fuzz_score:
                        #print("the keyword " + kw[0] + " matches with " + qws + " with root question word " + word + " score " + str(y))
                        max_fuzz_score = y
                        key_word_score = kw[1]  # also save the keyword_score in key_word_score
                        key_word_max = kw[0]
    return max_fuzz_score, key_word_score, key_word_max


def get_fuzz_score(KW, QW):
    return fuzz.partial_ratio(KW, QW)        # token_sort_ratio, partial_ratio, ratio, token_set_ratio, fuzzy_match


def get_names(result_tuple):
    text = ""
    i = 1
    for path in result_tuple:
        s = path[0]
        text = text + '\n' + str(i) + '. ' + (s.split('Keywords\\'))[1].split('.txt')[0]
        i = i + 1
    return text


def check_feature_list(question_words, n):
    import glob
    feature_list = glob.glob("D:\Phase 1\Feature Keywords/*.txt")
    feature_list_score = []
    f_count = 1
    analyse_list = []
    for FL in feature_list:  # taking each of the feature list
        print("\n \n$$$$$$$$$$$$$$$$$$$" + FL + "$$$$$$$$$$$$$$$$$$$$$$$$$ \n")
        fd = open(FL, 'r')
        keywords = fd.read().split("\n")
        keywords.pop(0)
        keywords.pop(-1)
        fl_score = 0
        key_word_list = ""
        question_word_score = 0
        key_word_score: float = 0

        for QW in question_words:  # taking each of the question words
            max_fl_score = 0
            max_fuzz_score = 0
            question_word_score = QW[1]
            #print("--------Checking for question Word---------- :" + QW[0])

            for KW in keywords:                                         # taking each keyword of the Feature List
                kw = KW.split(",")
                if kw[0] is None:
                    continue

                x = get_fuzz_score(kw[0], QW[0])                        # calculating the the match between words
                factor = 0.6 #(factor * float(x)) + ((1 - factor) * float(question_word_score) * float(kw[1]))
                temp_fl_score = (factor * float(x)) + ((1 - factor) * float(question_word_score) * float(kw[1]))

                if temp_fl_score > max_fl_score:
                    max_fl_score: float = temp_fl_score
                    max_fuzz_score = x
                    key_word_score = kw[1]
                    key_word_max = kw[0]

                #print("\t with keyword: " + kw[0])
                #print("\t max_fuzz_score is :" + str(max_fuzz_score))
                #print("\t key_word_max is :" + str(key_word_max))

                if max_fuzz_score == 100:
                    #print("\n gotcha!")
                    break

            if max_fuzz_score < 50:                                  # if the match is less than 75% check QW synonyms
                #print("___if score is less than 45____for the word " + QW[0])
                y: Tuple[int, int, str] = check_synonyms(QW[0], keywords, max_fuzz_score, key_word_score)
                if y[0] > max_fuzz_score:
                    max_fuzz_score = y[0]
                    key_word_score = y[1]
                    key_word_max = y[2]
                #print("\t with keyword: " + kw[0])
                #print("\t max_fuzz_score is :" + str(max_fuzz_score))
                #print("\t key_word_max is :" + str(key_word_max))
                max_fl_score = (factor * float(max_fuzz_score)) + (1 - factor) * float(question_word_score) * float(key_word_score)

            key_word_list = key_word_list + "," + key_word_max
            fl_score = fl_score + max_fl_score  # adding to FL_score
        print("\n \t \t" + str(fl_score) + "\n")
        feature_list_score.append(tuple([fd.name, fl_score, key_word_list]))
    return nlargest(n, feature_list_score, key=itemgetter(1))


def machine_learning_model(case, question_words, key_words, feature_path, *args):
    if case is 1:
        # the desired match is found in the list
        list1 = key_words.split(",")
        list1.pop(0)

        with open(feature_path, "r") as file:
            text = file.readlines()
        flag = 0
        while flag is 0:
            for key_word in list1:
                i = 0
                while i < len(text):
                    if key_word in text[i]:
                        temp_int = text[i].split(",", 1)[1]
                        if float(temp_int) < 10:
                            replace_int = float(temp_int) + 0.5
                        text[i] = text[i].replace(temp_int, str(replace_int)+"\n")
                    i = i + 1
            print(text)
            with open(feature_path, "w") as file:
                file.writelines(text)
            #if check_score(question_words, feature_path) >= score:
                flag = 1
        return None

    if case is 2:
        # the desired match is not found i the list
        #list2 = key_words.split(",")
        #list2.pop(0)
        print(question_words)
        print(key_words)
        with open(feature_path, "r") as file:
            text = file.readlines()
        flag = 0
        while flag is 0:
            key_word_count = 0
            for key_word in key_words:
                i = 0
                while i < len(text):
                    if key_word == "None of these ":
                        temp_text = str(question_words[key_word_count][0]) + "," + str(1.000000)
                        text.insert(len(text), temp_text)
                        print("yes")
                        break
                    if key_word == " question word Not relevant ":
                        break
                    if key_word == text[i].split(",")[0]:
                        if key_word == question_words[key_word_count][0]:
                            break
                        else:
                            temp_int = text[i].split(",", 1)[1]
                            temp_text = str(question_words[key_word_count][0]) + "," + temp_int
                            text.insert(i, temp_text)
                            break
                    i = i + 1
                key_word_count = key_word_count + 1
            print(text)
            with open(feature_path, "w") as file:
                file.writelines(text)
            # if check_score(question_words, feature_path) >= score:
            flag = 1
        return None


def fitment_analysis():
    return None


def main():
    window = Tk()
    window.title("Welcome to SunTec Product Management Tool")
    window.geometry('800x600')

    lbl = Label(window, text="Please select the Mode")
    lbl.grid(column=0, row=0)

    selected = IntVar()
    rad1 = Radiobutton(window, text='Training Mode', value=1, variable=selected)
    rad2 = Radiobutton(window, text='Testing Mode', value=2, variable=selected)

    def clicked():
        print(selected.get())
        if selected.get() == 1:
            window_train = Tk()
            window_train.title("Training Mode")
            lb_train = Label(window_train, text="Please describe the feature needed: ")
            lb_train.grid(column=1, row=0)
            txt_train_search = Entry(window_train, width=150)
            txt_train_search.grid(column=1, row=3)
            lb_train_output = Label(window_train, text="")
            lb_train_output.grid(column=1, row=4)
            btn_train_back = Button(window_train, text="Search another Feature")
            lb_train_ml1 = Label(window_train)
            selected1 = IntVar(window_train)
            rad_train_yes = Radiobutton(window_train, text="yes", value=1, variable=selected1)
            rad_train_no = Radiobutton(window_train, text="no", value=2, variable=selected1)
            btn_exit_train = Button(window_train, text='Exit', command=window_train.destroy)
            btn_train_ml1 = Button(window_train)
            btn_exit_train.grid(column=0, row=10)

            lb_train_feedback1 = Label(window_train, text=" Thanks for the feedback of above description/query, please click on ""search another feature"" button to continue ")
            lb_train_feedback2 = Label(window_train, text=" Please help us understand: ")
            mainframe = Frame(window_train)
            btn_train_ml_1 = Button(window_train, text="Train")
            btn_train_ml_2 = Button(window_train, text="Train")

            def click_back_train():
                lb_train.configure(text="Please describe the feature needed: ")
                txt_train_search.config(state=NORMAL)
                txt_train_search.delete(0, END)
                lb_train_output.config(text="")
                btn_train_search.grid(column=2, row=6)
                btn_train_back.grid_forget()
                lb_train_ml1.grid_forget()
                rad_train_yes.grid_forget()
                rad_train_no.grid_forget()
                btn_train_ml1.grid_forget()
                lb_train_feedback1.grid_forget()
                lb_train_feedback2.grid_forget()
                mainframe.grid_forget()
                btn_train_ml_1.grid_forget()
                btn_train_ml_2.grid_forget()

            def clicked_search():
                rake = Rake("data/stoplists/SmartStoplist.txt")
                question_words = rake.run(txt_train_search.get())
                result = check_feature_list(question_words, 25)
                result_display = get_names(result)

                lb_train.configure(text="Here are the suggestions for the entered question or description: ")
                txt_train_search.config(state=DISABLED)
                lb_train_output.configure(text=result_display)
                btn_train_back.config(state=NORMAL, command=click_back_train)
                btn_train_back.grid(column=1, row=10)
                btn_train_search.grid_forget()

                lb_train_ml1.config(text="Did you find the desired feature?")
                lb_train_ml1.grid(column=0, row=12)
                rad_train_yes.grid(column=1, row=12)
                rad_train_no.grid(column=1, row=13)

                def click_ml1():
                    print(selected1.get())
                    if selected1.get() == 1:
                        # ask for the choice
                        btn_train_ml1.config(state=DISABLED)
                                                 #
                        mainframe.grid(column=0, row=16, sticky=(N, W, E, S))
                        # Create a Tkinter variable
                        tkvar = StringVar(window_train)

                        # Dictionary with options
                        choice_list = result_display.split("\n")
                        tkvar.set(choice_list[0])  # set the default option

                        popupMenu = OptionMenu(mainframe, tkvar, *choice_list)
                        Label(mainframe, text="Choose the Feature").grid(row=1, column=1)
                        popupMenu.grid(row=1, column=3)

                        def train():
                            print(tkvar.get())
                            a = int(tkvar.get().split(". ", 1)[0])
                            machine_learning_model(1, question_words, result[a-1][2], result[a-1][0], result[2][1])
                            lb_train_feedback1.grid(column=1, row=20)

                        btn_train_ml_1.config(command=train)
                        btn_train_ml_1.grid(row=19, column=3)

                    if selected1.get() == 2:
                        import glob
                        feature_list = glob.glob("D:\Phase 1\Feature Keywords/*.txt")
                        i = 0
                        text = ""
                        for path in feature_list:
                            print(path)
                            text = text + '\n' + str(i) + '. ' + (path.split('Keywords\\'))[1].split('.txt')[0]
                            i = i + 1
                        mainframe.grid(column=0, row=16, sticky=(N, W, E, S))
                        # Create a Tkinter variable
                        tkvar = StringVar(window_train)

                        # Dictionary with options
                        choice_list = text.split("\n")
                        tkvar.set(choice_list[0])  # set the default option

                        popupMenu = OptionMenu(mainframe, tkvar, *choice_list)
                        Label(mainframe, text="Choose the Feature").grid(row=1, column=1)
                        popupMenu.grid(row=1, column=3)

                        def train2():
                            print(tkvar.get())
                            print(question_words)

                            path = "D:\Phase 1\Feature Keywords/" + tkvar.get().split(". ", 1)[1] + ".txt"
                            fd = open(path, 'r')
                            keywords_ml = fd.read().split("\n")
                            keywords_ml.pop(0)
                            keywords_ml.pop(-1)
                            print(keywords_ml)

                            labels = []

                            def myClick():
                                del labels[:]  # remove any previous labels from if the callback was called before
                                myframe = Frame(window_train, relief=GROOVE)
                                myframe.grid(column=0, row=21, sticky=(N, W, E, S))
                                k = 0

                                tkvar1 = []

                                choice_list1 = []
                                # Dictionary with options
                                for z in keywords_ml:
                                    choice_list1.append(z.split(",")[0])

                                choice_list1.append("None of these ")
                                choice_list1.append(" question word Not relevant ")

                                print(choice_list1)
                                for j in question_words:
                                    labels.append(Label(myframe, text="By the word ' " + j[0] + " 'you mean: \n "))
                                    labels[k].grid(row=22+k, column=1)
                                    tkvar1temp = StringVar(window_train)
                                    tkvar1.append(tkvar1temp)
                                    tkvar1[k].set(choice_list1[0])
                                    popupMenu1 = OptionMenu(myframe, tkvar1[k], choice_list1[0], *choice_list1)
                                    popupMenu1.grid(row=22+k, column=2)
                                    k = k + 1

                                def change():
                                    index = 0
                                    keywords_ml2 = []
                                    while index < len(tkvar1):
                                        keywords_ml2.append(tkvar1[index].get())
                                        index = index + 1
                                    machine_learning_model(2, question_words, keywords_ml2, path)
                                    print(question_words)
                                    print(keywords_ml2)

                                mybutton_submit = Button(window_train, text="Submit", command=change).grid(row=24, column=2)
                            mybutton = Button(window_train, text="OK", command=myClick).grid(row=20, column=2)
                            lb_train_feedback2.grid(row=20, column=1)
                            #machine_learning_model(1, question_words, result[a-1][2], result[a-1][0], result[2][1])

                        btn_train_ml_2.config(command=train2)
                        btn_train_ml_2.grid(row=19, column=2)
                        choice = 2
                        # machine_learning_model(1, question_words, result[choice][0], result[2][1])

                btn_train_ml1.config(text="Submit", command=click_ml1)
                btn_train_ml1.grid(column=2, row=12)

            btn_train_search = Button(window_train, text="Search", command=clicked_search)
            btn_train_search.grid(column=2, row=10)
            window_train.mainloop()

        if selected.get() == 2:
            window_test = Tk()
            window_test.title("Testing Mode")
            lb_test = Label(window_test, text="Please describe the feature needed: ")
            lb_test.grid(column=1, row=0)
            txt_test_search = Entry(window_test, width=150)
            txt_test_search.grid(column=1, row=3)
            lb_test_output = Label(window_test, text="")
            lb_test_output.grid(column=1, row=4)
            mainframe2 = Frame(window_test)
            status = Label(window_test, text="It does work ...!!", relief=SUNKEN, anchor=W)
            status.grid(row=20, sticky='NSE')
            btn_test_submit = Button(mainframe2)
            btn_test_submit_2 = Button(mainframe2)

            def click_back_test():
                lb_test.configure(text="Please describe the feature needed: ")
                txt_test_search.delete(0, END)
                lb_test_output.config(text="")
                mainframe2.grid_forget()
                btn_test_submit_2.grid_forget()

            def clicked_search():
                lb_test.configure(text="Here are the suggestions for the entered question or description:")
                rake = Rake("data/stoplists/SmartStoplist.txt")
                question_words = rake.run(txt_test_search.get())
                result = check_feature_list(question_words, 8)
                result_display = get_names(result)
                print(question_words)
                lb_test_output.configure(text=result_display)
                # print(check_feature_list(question_words))

                mainframe2.grid(column=1, row=5, sticky=(N, W, E, S))
                # Create a Tkinter variable
                tkvar_test_1 = StringVar(window_test)

                # Dictionary with options
                choice_list = result_display.split("\n")
                choice_list.append("Not found")

                popupmenu1 = OptionMenu(mainframe2, tkvar_test_1, choice_list[0], *choice_list)
                Label(mainframe2, text="Which feature suits the requirement?").grid(row=12, column=0)
                popupmenu1.grid(row=12, column=1)

                def click_test_2():
                    Label(mainframe2, text="Enter the requirement  ").grid(row=14, column=0)
                    tkvar_test_2 = IntVar(window_test)
                    popupmenu2 = OptionMenu(mainframe2, tkvar_test_2, [1], [2], [3], [4], [5]).grid(row=14, column=1)
                    Label(mainframe2, text=" and sub-requirement ").grid(row=14, column=2)
                    tkvar_test_3 = IntVar(window_test)
                    popupmenu3 = OptionMenu(mainframe2, tkvar_test_3, [1], [2], [3], [4], [5]).grid(row=14, column=3)
                    print(tkvar_test_1.get())
                    btn_test_submit_2.config(text="commit", command=print("1"))
                    btn_test_submit_2.grid(column=4, row=14)

                btn_test_submit.config(text="Submit", command=click_test_2)
                btn_test_submit.grid(column=3, row=12)

                btn_test_back = Button(window_test, text="Search another feature", command=click_back_test)
                btn_test_back.grid(column=0, row=14)

            btn_test_search = Button(window_test, text="Search", command=clicked_search)
            btn_test_search.grid(column=2, row=14)

            window_test.mainloop()
    btn_go = Button(window, text=" Go !!", command=clicked)
    btn_exit = Button(window, text='Exit', command=window.destroy)
    rad1.grid(column=4, row=3)
    rad2.grid(column=4, row=5)
    btn_go.grid(column=5, row=7)
    btn_exit.grid(column=7, row=7)

    window.mainloop()


if __name__ == "__main__":
    main()

