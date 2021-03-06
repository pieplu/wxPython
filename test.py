#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import codecs
import re
import sqlite3
import wx
import wx.dataview as dv



#### Fonctions ##########



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

### Optimisation avec Sylvain -----------------
def fais_le(c, tbl, transforms):
    tr = transforms
    for row in c.execute("SELECT * FROM %s"%tbl):
        while True:
            row = c.fetchone()
            if row == None:
                break
            yield [tr[i](row[i]) for i in range(2)]

# Une fonction qui convertit une string, l'autre pas
ff, fn = lambda s: s.encode('utf-8'), lambda s: s



def search(c,syl):
    for ligne in c.execute("SELECT * FROM syllabes WHERE syllabe = '%s'"%syl):
        while True:
            ligne = c.fetchone()
            if ligne == None:
                break
            yield ligne[0].encode('utf-8'), str(ligne[1])



### PROGRAMME


connection = sqlite3.connect('basedonnees.db')
c = connection.cursor()

lecture_syllabes(c, '010_C7.xml')
connection.commit()




#extraction_db(c)


liste_test = []

for syl, nb in fais_le(c, tbl='syllabes', transforms=(ff,fn)):
        liste_test.append([syl, str(nb)])


print len(liste_test) #la bd est complètement rechargé à chaque execution, à voir



### Interface

class ExamplePanel(wx.Panel):
    def __init__(self, parent):
        #extraction_syllabes(c)


        wx.Panel.__init__(self, parent)
        #self.quote = wx.StaticText(self, label="Your quote :", pos=(20, 30))

        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self, pos=(400,20), size=(150,60), style=wx.TE_MULTILINE | wx.TE_READONLY)



        # the edit control - one line version.
       # self.lblname = wx.StaticText(self, label="Your name :", pos=(20,60))
       # self.editname = wx.TextCtrl(self, value="Enter here your name", pos=(150, 60), size=(140,-1))

        self.dvlc = dvlc = dv.DataViewListCtrl(self, size=(200,200), pos=(0,100))

        dvlc.AppendTextColumn('Sylabe', width=70)
        dvlc.AppendTextColumn('Occurence', width=70)

        for itemvalues in liste_test:
            dvlc.AppendItem(itemvalues)


        #ajout à la liste du tableau


        #the edit control - one line version.
        self.lblname = wx.StaticText(self, label="Recherche :", pos=(20,20))
        self.editname = wx.TextCtrl(self, value="de", pos=(110, 20), size=(140,-1))
        # A button
        self.button =wx.Button(self, label="Rechercher", pos=(260, 20))
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.button)

        self.buttonTake =wx.Button(self, label="Prendre", pos=(260, 50))
        self.Bind(wx.EVT_BUTTON, self.selectElem,self.buttonTake)






    def OnClick(self,event):
        str_recherche = self.editname.GetValue()
        tab_search = search(c,str_recherche)
        for itemvalues in tab_search:
            self.dvlc.AppendItem(itemvalues)
            self.logger.AppendText('item: %s\n' % itemvalues[0])

    def selectElem(self,event):
        id = self.dvlc.GetSelectedRow()
        val = self.dvlc.GetTextValue(id, 0)
        self.logger.AppendText('item: %s\n' % val)




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