#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import sqlite3
import wx


#### Fonctions ##########



### Optimisation avec Sylvain -----------------
def fais_le(c, tbl, transforms):
    tr = transforms
    for row in c.execute("SELECT * FROM %s"%tbl):
        while True:
            row = c.fetchone()
            if row == None:
                break

            yield [tr[i](row[i]) for i in range(1)]


# Une fonction qui convertit une string, l'autre pas
ff, fn = lambda s: s.encode('utf-8'), lambda s: s

params = (
    { 'tbl':'syllabes', 'transforms':(ff,ff,ff) },
    { 'tbl':'syllabes_precedentes', 'transforms':(ff,ff,ff) },
    { 'tbl':'syllabes_suivantes', 'transforms':(ff,ff,ff)}
)


#
##### FIN optimisation -----------------
def extraction_db(c):

    for row in c.execute("SELECT * FROM syllabes"):
        while True:
            row = c.fetchone()
            if row == None:
                break
            print row[0].encode('utf-8'), row[1], row[2]
    for row in c.execute("SELECT * FROM syllabes_precedentes"):
        while True:
            row = c.fetchone()
            if row == None:
                break
            print row[0].encode('utf-8'), row[1].encode('utf-8'), row[2]
    for row in c.execute("SELECT * FROM syllabes_suivantes"):
        while True:
            row = c.fetchone()
            if row == None:
                break
            print row[0].encode('utf-8'), row[1].encode('utf-8'), row[2]
    return None


def extraction_syllabes(c):
    for row in c.execute("SELECT * FROM syllabes"):
        while True:
            row = c.fetchone()
            if row == None:
                break
            print row[0].encode('utf-8'), row[1], row[2]





def lecture_syllabes(c, fichier):


    c.execute("CREATE TABLE IF NOT EXISTS syllabes(syllabe TEXT, frequence INT, structure TEXT)")
    c.execute(
        "CREATE TABLE IF NOT EXISTS syllabes_precedentes (syllabe_1 TEXT, syl_precedente TEXT, frequence_paire INT)")
    c.execute("CREATE TABLE IF NOT EXISTS syllabes_suivantes (syllabe_2 TEXT, syl_suivante TEXT, freq_paire INT)")
    dico_syllabes = {}
    dico_syl_prec = {}
    dico_syl_suiv = {}
    fichier = codecs.open(fichier, 'r', encoding='utf-8')
    texte = fichier.read()
    fichier.close()

    exp_nb_syllabes = re.compile(r'<tour_de_parole>.+?</tour_de_parole>', flags=re.UNICODE | re.DOTALL)
    exp_syllabes = re.compile(r'<tour_de_parole>\s*|\s*</tour_de_parole>')
    exp_syllabes_seules = re.compile(r' *[ |] *')
    total_syllabes = 0
    liste_trans_syllabes = re.findall(exp_nb_syllabes, texte)

    for elem in liste_trans_syllabes:
        trans_syllabes = re.sub(exp_syllabes, '', elem)
        syllabes_separees = re.split(exp_syllabes_seules, trans_syllabes)
        total_syllabes += len(syllabes_separees)
        for syl in syllabes_separees:
            if syl not in dico_syllabes:
                dico_syllabes[syl] = 1
            else:
                dico_syllabes[syl] += 1
        for i in range(1, (len(syllabes_separees) - 1)):
            if (syllabes_separees[i], syllabes_separees[i - 1]) not in dico_syl_prec:
                dico_syl_prec[(syllabes_separees[i], syllabes_separees[i - 1])] = 1
            else:
                dico_syl_prec[(syllabes_separees[i], syllabes_separees[i - 1])] += 1
        for i in range(len(syllabes_separees) - 1):
            if (syllabes_separees[i], syllabes_separees[i + 1]) not in dico_syl_suiv:
                dico_syl_suiv[(syllabes_separees[i], syllabes_separees[i + 1])] = 1
            else:
                dico_syl_suiv[(syllabes_separees[i], syllabes_separees[i + 1])] += 1

    syllabes_triees = sorted(dico_syllabes, key=dico_syllabes.get, reverse=True)
    syllabes_tuples = []
    for syl in syllabes_triees:
        syllabes_tuples.append((syl, dico_syllabes[syl], "null"))

    c.executemany("INSERT INTO syllabes VALUES(?, ?, ?)", syllabes_tuples)
    syllabes_prec_triees = sorted(dico_syl_prec, key=dico_syl_prec.get, reverse=True)
    syllabes_prec_tup = []

    for i in range(len(syllabes_prec_triees)):
        syllabes_prec_tup.append(
            (syllabes_prec_triees[i][0], syllabes_prec_triees[i][1], dico_syl_prec[syllabes_prec_triees[i]]))

    c.executemany("INSERT INTO syllabes_precedentes VALUES(?, ?, ?)", syllabes_prec_tup)
    #for i in range(len(syllabes_prec_tup)):
    #    print syllabes_prec_tup[i][0].encode('utf-8'), syllabes_prec_tup[i][1].encode('utf-8'), syllabes_prec_tup[i][2]
    syllabes_suiv_triees = sorted(dico_syl_suiv, key=dico_syl_suiv.get, reverse=True)
    syllabes_suiv_tup = []

    for i in range(len(syllabes_suiv_triees)):
        syllabes_suiv_tup.append(
            (syllabes_suiv_triees[i][0], syllabes_suiv_triees[i][1], dico_syl_suiv[syllabes_suiv_triees[i]]))

    c.executemany("INSERT INTO syllabes_suivantes VALUES(?, ?, ?)", syllabes_suiv_tup)
    #for i in range(len(syllabes_suiv_tup)):
    #    print syllabes_suiv_tup[i][0].encode('utf-8'), syllabes_suiv_tup[i][1].encode('utf-8'), syllabes_suiv_tup[i][2]




### PROGRAMME


connection = sqlite3.connect('basedonnees.db')
c = connection.cursor()

lecture_syllabes(c, '010_C7.xml')
connection.commit()


#extraction_db(c)
res = []
for param in params:
    for syl1 in fais_le(c, **param):
        res.append(syl1)











### Interface

class ExamplePanel(wx.Panel):
    def __init__(self, parent):
        #extraction_syllabes(c)

        wx.Panel.__init__(self, parent)
        self.quote = wx.StaticText(self, label="Your quote :", pos=(20, 30))

        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # A button
        self.button =wx.Button(self, label="Save", pos=(200, 325))
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.button)

        # the edit control - one line version.
        self.lblname = wx.StaticText(self, label="Your name :", pos=(20,60))
        self.editname = wx.TextCtrl(self, value="Enter here your name", pos=(150, 60), size=(140,-1))


        # the combobox Control
        self.sampleList = res
        self.lblhear = wx.StaticText(self, label="How did you hear from us ?", pos=(20, 90))
        self.edithear = wx.ComboBox(self, pos=(150, 90), size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.edithear)




    def EvtComboBox(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())
    def OnClick(self,event):
        self.logger.AppendText('Evtclick: %s\n' % event.GetString())



class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,400))

app = wx.App(False)
frame = MyFrame(None, 'Appli')
panel = ExamplePanel(frame)
frame.Show()
app.MainLoop()




connection.close()