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
        row = c.fetchone()
        if row:
            print row[0].encode('utf-8'), row[1]
    for row in c.execute("SELECT * FROM syllabes_precedentes"):
        row = c.fetchone()
        if row:
            print row[0].encode('utf-8'), row[1].encode('utf-8'), row[2]
    for row in c.execute("SELECT * FROM syllabes_suivantes"):
        row = c.fetchone()
        if row:
            print row[0].encode('utf-8'), row[1].encode('utf-8'), row[2]
    return None




def lecture_syllabes(c, fichier):


    c.execute("CREATE TABLE IF NOT EXISTS syllabes(syllabe TEXT, frequence INT)")
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
        syllabes_tuples.append((syl, dico_syllabes[syl]))



    for sylInsert, nbSyl in syllabes_tuples:
        c.execute("SELECT * FROM syllabes WHERE syllabe = '%s'"%sylInsert)
        if (c.fetchone()):
            print "if " + sylInsert
            c.execute("UPDATE syllabes SET frequence="+unicode(nbSyl)+" WHERE syllabe='"+sylInsert+"'")
        else:
            print "else " + sylInsert
            insertion = [sylInsert, nbSyl]
            c.execute("INSERT INTO syllabes VALUES("?, ?)")




    c.executemany("INSERT INTO syllabes VALUES(?, ?)", syllabes_tuples)
    syllabes_prec_triees = sorted(dico_syl_prec, key=dico_syl_prec.get, reverse=True)
    syllabes_prec_tup = []

    for i in range(len(syllabes_prec_triees)):
        syllabes_prec_tup.append(
            (syllabes_prec_triees[i][0], syllabes_prec_triees[i][1], dico_syl_prec[syllabes_prec_triees[i]]))

    c.executemany("INSERT INTO syllabes_precedentes VALUES(?, ?, ?)", syllabes_prec_tup)
    syllabes_suiv_triees = sorted(dico_syl_suiv, key=dico_syl_suiv.get, reverse=True)
    syllabes_suiv_tup = []

    for i in range(len(syllabes_suiv_triees)):
        syllabes_suiv_tup.append(
            (syllabes_suiv_triees[i][0], syllabes_suiv_triees[i][1], dico_syl_suiv[syllabes_suiv_triees[i]]))

    c.executemany("INSERT INTO syllabes_suivantes VALUES(?, ?, ?)", syllabes_suiv_tup)

### Optimisation avec Sylvain -----------------
def fais_le(c, tbl, transforms):
    tr = transforms
    for row in c.execute("SELECT * FROM %s"%tbl):
        row = c.fetchone()
        if row:
            yield [tr[i](row[i]) for i in range(2)]

# Une fonction qui convertit une string, l'autre pas
ff, fn = lambda s: s.encode('utf-8'), lambda s: s



def search(c,syl):
    for ligne in c.execute("SELECT * FROM syllabes WHERE syllabe = '%s'"%syl):
        ligne = c.fetchone()
        if ligne:
            yield ligne[0].encode('utf-8'), str(ligne[1])



### PROGRAMME


connection = sqlite3.connect('basededonnees.db')
c = connection.cursor()

lecture_syllabes(c, '010_C7.xml')
connection.commit()

result = search(c, "qu")
print result

#extraction_db(c)


liste_test = []

for syl, nb in fais_le(c, tbl='syllabes', transforms=(ff,fn)):
        liste_test.append([syl.decode('utf-8'), unicode(nb)])


print len(liste_test) #la bd est complètement rechargé à chaque execution, à voir



### Interface





class TestLayoutConstraints(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.SetAutoLayout(True)


        self.panelA = wx.Window(self, -1, style=wx.SIMPLE_BORDER)

        txt = wx.StaticText(
                    self.panelA, -1,
                    "Recherche",
                    (20,20), (-1, 50)
                    )


        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, 0)
        lc.left.SameAs(self, wx.Left, 0)
        lc.bottom.PercentOf(self, wx.Bottom, 35)
        lc.right.SameAs(self, wx.Right, 0)
        self.panelA.SetConstraints(lc)
        
        self.panelA.logger = wx.TextCtrl(self, pos=(400,20), size=(150,60), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.panelA.editname = wx.TextCtrl(self, value="...", pos=(110, 20), size=(140,-1))
        self.panelA.button =wx.Button(self, label="Rechercher", pos=(260, 17))        

        self.panelB = wx.Window(self, -1, style=wx.SIMPLE_BORDER)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.panelA, 0)
        lc.right.PercentOf(self, wx.Right, 34)
        lc.bottom.SameAs(self, wx.Bottom, 0)
        lc.left.SameAs(self, wx.Left, 0)
        self.panelB.SetConstraints(lc)
        
        self.panelB.dvlc = dvlc = dv.DataViewListCtrl(self.panelB, size=(200,200), pos=(0,0))
        
        dvlc.AppendTextColumn('Syllabe', width=75)
        dvlc.AppendTextColumn('Occurrence', width=75)
        
        for itemvalues in liste_test:
            dvlc.AppendItem(itemvalues)
            


        self.panelC = wx.Window(self, -1, style=wx.SIMPLE_BORDER)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.panelA, 0)
        lc.right.PercentOf(self, wx.Right, 67)
        lc.bottom.SameAs(self, wx.Bottom, 0)
        lc.left.RightOf(self.panelB, 0)
        self.panelC.SetConstraints(lc)
        
        wx.StaticText(
            self.panelC, -1, "Paires syllabes précédentes", (4, 4)
            )
         
        self.panelD = wx.Window(self, -1, style=wx.SIMPLE_BORDER)
        wx.StaticText(
            self.panelD, -1, "Paires syllabes suivantes", (4, 4)
            )
        
        lc = wx.LayoutConstraints()
        lc.bottom.SameAs(self, wx.Bottom, 0)
        lc.right.SameAs(self, wx.Right, 0)
        lc.left.RightOf(self.panelC, 0)
        lc.top.Below(self.panelA, 0)
        self.panelD.SetConstraints(lc)


        
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.panelA.button)

        
    def OnClick(self,event):
        self.panelA.logger.AppendText('Evtclick: %s\n' % event.GetString())





    #def OnClick(self,event):
    #    str_recherche = self.editname.GetValue()
    #    tab_search = search(c,str_recherche)
    #    for itemvalues in tab_search:
    #        self.dvlc.AppendItem(itemvalues)
    #



class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,400))

app = wx.App(False)
frame = MyFrame(None, 'Application syllabes')
panel = TestLayoutConstraints(frame)
frame.Show()
app.MainLoop()




connection.close()