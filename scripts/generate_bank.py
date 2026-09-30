#!/usr/bin/env python3
"""Build the 180-question SVT bank from the supplied brief plus clearly marked complements."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "source-brief.txt"
OUT = ROOT / "questions.json"
THEMES = {
    "nutrition": {"title": "Nutrition et santé", "provided": [], "questions": []},
    "genetics": {"title": "Information génétique", "provided": [], "questions": []},
    "earth": {"title": "Dynamique du globe terrestre et évolution biologique", "provided": [], "questions": []},
}

def make_tf(theme, qid, prompt, truth, explanation, origin):
    return {"id": qid, "type": "vrai-faux", "question": prompt,
            "options": ["Vrai", "Faux"], "reponses_correctes": [0 if truth else 1],
            "explication": explanation, "origine": origin, "theme": theme}

def explain_source_tf(theme, qid, statement, truth):
    if truth:
        return f"Vrai : {statement} Cette propriété correspond à la notion de cours évaluée."
    return "Faux : la phrase confond une étape, une structure ou une fonction. Reprends les mots-clés du cours pour identifier ce qui doit être corrigé."

current = None
for raw in SOURCE.read_text(encoding="utf-8").splitlines():
    if "THÈME 1 : NUTRITION" in raw.upper(): current = "nutrition"; continue
    if "THÈME 2 : INFORMATION GÉNÉTIQUE" in raw.upper(): current = "genetics"; continue
    if "THÈME 3" in raw.upper(): current = "earth"; continue
    if not current: continue
    m = re.match(r"\s*(\d+)\.\s*(.*)$", raw)
    if not m: continue
    qid, body = int(m.group(1)), m.group(2).strip()
    ans_match = re.search(r"\*\*Réponse\s*:\s*(.*?)\*\*", body, re.I)
    answer_text = ans_match.group(1).strip() if ans_match else ""
    clean = body[:ans_match.start()].strip() if ans_match else body
    if "**Définition**" in clean:
        statement = clean.replace("**Définition**", "").strip()
        prompt = f"{statement} — cette définition est-elle correcte ?"
        obj = make_tf("nutrition" if current == "nutrition" else current, qid, prompt, True,
                      "Oui. La formulation reprend correctement la définition scientifique de la notion citée.", "fourni")
        THEMES[current]["provided"].append(obj)
    elif "**Vrai/Faux**" in clean:
        statement = clean.replace("**Vrai/Faux**", "").strip()
        truth = answer_text.lower().startswith("vrai")
        obj = make_tf(current, qid, statement, truth, explain_source_tf(current, qid, statement, truth), "fourni")
        THEMES[current]["provided"].append(obj)
    else:
        spans = list(re.finditer(r"(?<![\w])([a-d])\)\s*", clean, re.I))
        if not spans:
            continue
        prompt = clean[:spans[0].start()].rstrip(" :")
        options = []
        for i, span in enumerate(spans):
            end = spans[i+1].start() if i + 1 < len(spans) else len(clean)
            options.append(clean[span.end():end].strip().rstrip(" ."))
        labels = [x.lower() for x in re.findall(r"[a-d]", answer_text.lower())]
        correct = [ord(x)-97 for x in labels]
        if not prompt or not options or not correct or max(correct) >= len(options):
            continue
        good = "; ".join(f"« {options[i]} »" for i in correct)
        obj = {"id": qid, "type": "qcm", "question": prompt, "options": options,
               "reponses_correctes": correct,
               "explication": f"Les bonnes propositions sont {good}. Elles répondent à la propriété demandée ; compare chaque distracteur à la définition ou au mécanisme du cours.",
               "origine": "fourni"}
        obj["theme"] = current
        THEMES[current]["provided"].append(obj)

# Explicit corrections for false source statements, where the original handout gave only Vrai/Faux.
FALSE_EXPLANATIONS = {
    ("nutrition", 9): "Faux : les vitamines sont des micronutriments indispensables, mais elles ne fournissent pas d’énergie. L’énergie vient notamment des glucides, lipides et protides.",
    ("nutrition", 11): "Faux : la digestion des protéines commence dans l’estomac et se poursuit dans l’intestin grêle grâce à d’autres enzymes.",
    ("nutrition", 12): "Faux : l’activité enzymatique dépend aussi du pH, de la température et de la concentration en substrat, entre autres facteurs.",
    ("nutrition", 13): "Faux : les villosités intestinales augmentent la surface d’absorption ; la digestion se déroule dans la lumière du tube digestif.",
    ("nutrition", 14): "Faux : les quantités indiquées ne correspondent pas à une ration équilibrée ; les besoins dépendent de la personne et les glucides ne se limitent pas à 50–80 g.",
    ("nutrition", 16): "Faux : le désoxyribose est un pentose (5 carbones), et non un hexose.",
    ("nutrition", 20): "Faux : l’athérosclérose correspond à des plaques dans la paroi des artères, pas dans les espaces sous-cutanés.",
    ("nutrition", 21): "Faux : les animaux stockent le glucose sous forme de glycogène ; les végétaux stockent surtout l’amidon.",
    ("nutrition", 22): "Faux : l’excès de poids est associé à un risque plus élevé d’hypertension, pas plus faible.",
    ("nutrition", 24): "Faux : le galactose est un hexose de formule C₆H₁₂O₆.",
    ("nutrition", 28): "Faux : l’huile d’olive est principalement un mélange de triglycérides (lipides simples), et non un lipide complexe.",
    ("nutrition", 30): "Faux : l’anorexie mentale est un trouble du comportement alimentaire et ne se réduit pas à une carence involontaire.",
    ("nutrition", 33): "Faux : le kwashiorkor est principalement associé à une carence sévère en protéines, souvent dans un contexte de malnutrition.",
    ("genetics", 12): "Faux : chez les cellules eucaryotes, la transcription a lieu dans le noyau ; l’ARNm rejoint ensuite le cytoplasme.",
    ("genetics", 13): "Faux : la traduction a lieu dans le cytoplasme, sur les ribosomes, à partir de l’ARNm.",
}

for (theme_id, question_id), explanation in FALSE_EXPLANATIONS.items():
    for question in THEMES[theme_id]["provided"]:
        if question["id"] == question_id:
            question["explication"] = explanation

# Small accuracy edits to avoid teaching known misconceptions from the supplied answer key.
SOURCE_REVISIONS = {
    ("nutrition", 3): {
        "reponses_correctes": [3],
        "explication": "Un acide aminé est un constituant des protéines. L’hydrolyse d’une protéine libère des acides aminés ; un acide aminé n’est pas lui-même un polymère hydrolysable en acides aminés.",
        "note_pedagogique": "La clé fournie incluait b ; elle a été corrigée, car l’hydrolyse des protéines libère les acides aminés.",
    },
    ("nutrition", 8): {
        "options": ["des oses", "certains acides aminés aromatiques", "des acides gras", "de l’amidon"],
        "explication": "La réaction xanthoprotéique met en évidence des noyaux aromatiques, présents dans certains acides aminés comme la tyrosine ou le tryptophane.",
        "note_pedagogique": "Le choix fourni « acides aminés » a été précisé : la réaction concerne certains acides aminés aromatiques, pas tous.",
    },
    ("genetics", 7): {
        "reponses_correctes": [0, 1],
        "explication": "L’albinisme est héréditaire et résulte d’une diminution ou d’une absence de mélanine. Les mélanocytes sont généralement présents ; c’est leur production de mélanine qui est altérée.",
        "note_pedagogique": "La clé fournie incluait l’absence de mélanocytes ; cette proposition a été retirée pour ne pas confondre albinisme et absence de cellules pigmentaires.",
    },
    ("genetics", 48): {
        "question": "Dans une maladie autosomale récessive, un individu atteint a généralement hérité d’un allèle muté de chacun de ses parents.",
        "explication": "Dans le modèle autosomal récessif classique, l’individu atteint possède deux copies altérées du gène, une héritée de chaque parent.",
        "note_pedagogique": "L’énoncé fourni a été reformulé : les parents ne sont pas nécessairement tous deux des porteurs non atteints.",
    },
}
for (theme_id, question_id), changes in SOURCE_REVISIONS.items():
    for question in THEMES[theme_id]["provided"]:
        if question["id"] == question_id:
            question.update(changes)

def explain_source_tf(theme, qid, statement, truth):
    if not truth and (theme, qid) in FALSE_EXPLANATIONS:
        return FALSE_EXPLANATIONS[(theme, qid)]
    if truth:
        return f"Vrai : {statement} Cette propriété correspond à la notion de cours évaluée."
    return "Faux : la phrase confond une étape, une structure ou une fonction. Reprends les mots-clés du cours pour identifier ce qui doit être corrigé."

def mcq(theme, qid, question, options, correct, explanation):
    return {"id": qid, "type": "qcm", "question": question, "options": options,
            "reponses_correctes": correct, "explication": explanation,
            "origine": "complément", "theme": theme}

def vf(theme, qid, question, truth, explanation):
    return make_tf(theme, qid, question, truth, explanation, "complément")

# Twelve Genetics questions were absent from the supplied attachment (it ends at item 48).
GENETICS = [
    mcq("genetics",49,"Dans une cellule somatique humaine, combien de chromosomes trouve-t-on généralement ?",["46 chromosomes, organisés en 23 paires","23 chromosomes organisés en 46 paires","44 chromosomes, sans chromosomes sexuels","92 paires de chromosomes"],[0],"La plupart des cellules somatiques humaines possèdent 46 chromosomes, répartis en 23 paires ; les gamètes en possèdent 23."),
    mcq("genetics",50,"Dans l’ADN, quelles bases sont complémentaires ?",["A avec T, et C avec G","A avec C, et T avec G","A avec U, et C avec G","A avec G, et T avec C"],[0],"Dans l’ADN, l’adénine s’apparie avec la thymine et la cytosine avec la guanine."),
    vf("genetics",51,"Lors de la réplication semi-conservative, chaque molécule d’ADN fille contient un brin ancien et un brin nouvellement synthétisé.",True,"Chaque brin parental sert de modèle ; les deux molécules obtenues conservent chacune un brin d’origine."),
    mcq("genetics",52,"Quel est le rôle principal de l’ARN messager ?",["Transporter l’information copiée d’un gène vers un ribosome","Former la membrane de la cellule","Stocker les lipides","Détruire les chromosomes"],[0],"L’ARNm transporte une copie de l’information génétique jusqu’au ribosome, où elle sert de modèle à la synthèse d’une protéine."),
    vf("genetics",53,"L’anticodon d’un ARNt peut s’apparier avec un codon complémentaire de l’ARNm.",True,"La complémentarité codon–anticodon permet d’apporter au ribosome l’acide aminé correspondant."),
    mcq("genetics",54,"Un chromosome eucaryote est principalement constitué :",["D’ADN associé à des protéines","D’ARN uniquement","De lipides et de glucose","D’une seule protéine"],[0],"Un chromosome est une longue molécule d’ADN organisée avec des protéines, notamment des histones."),
    vf("genetics",55,"Chez tous les individus d’une même espèce, chaque gène possède nécessairement le même allèle.",False,"Faux : un gène peut exister sous plusieurs versions appelées allèles, ce qui contribue à la diversité génétique."),
    vf("genetics",56,"La méiose réduit de moitié le nombre de chromosomes des cellules qui deviennent des gamètes.",True,"La méiose fait passer d’une cellule diploïde à des cellules haploïdes, qui contiennent un seul exemplaire de chaque paire."),
    vf("genetics",57,"Un crossing-over peut échanger des segments entre chromosomes homologues en prophase I de méiose.",True,"Cet échange, ou brassage intrachromosomique, crée de nouvelles associations d’allèles."),
    vf("genetics",58,"Les deux allèles d’un gène autosomal se séparent lors de la formation des gamètes.",True,"Chaque gamète ne reçoit qu’un seul des deux allèles d’un gène autosomal, selon la ségrégation des chromosomes homologues."),
    vf("genetics",59,"Pour une maladie autosomale récessive, un individu hétérozygote peut être porteur sans présenter la maladie.",True,"Dans le modèle récessif classique, une seule copie de l’allèle muté ne suffit généralement pas à exprimer le phénotype malade."),
    vf("genetics",60,"Le phénotype peut dépendre à la fois du génotype et de l’environnement.",True,"Les caractères observables résultent de l’expression des gènes dans un environnement donné ; leur importance varie selon le caractère."),
]

# Sixty original questions for the missing Earth dynamics and biological evolution theme.
EARTH = [
    mcq("earth",1,"Quelles sont les trois grandes enveloppes internes de la Terre ?",["Croûte, manteau et noyau","Atmosphère, hydrosphère et biosphère","Lithosphère, stratosphère et noyau","Croûte, océan et magma"],[0],"La structure interne est classiquement décrite en croûte, manteau et noyau ; chaque enveloppe a une composition et des propriétés distinctes."),
    vf("earth",2,"La lithosphère comprend la croûte et la partie supérieure rigide du manteau.",True,"La lithosphère est l’enveloppe mécanique rigide découpée en plaques."),
    vf("earth",3,"L’asthénosphère est une couche entièrement liquide sur laquelle flottent les plaques.",False,"Faux : l’asthénosphère est solide mais ductile à l’échelle géologique ; elle peut se déformer lentement."),
    vf("earth",4,"Les plaques lithosphériques se déplacent les unes par rapport aux autres.",True,"Les mouvements lents des plaques expliquent notamment l’ouverture des océans, les subductions et les failles transformantes."),
    mcq("earth",5,"À une limite divergente entre deux plaques océaniques, on observe généralement :",["La formation de nouvelle lithosphère au niveau d’une dorsale","La disparition de toute activité magmatique","La collision de deux continents","La plongée systématique d’une plaque continentale"],[0],"À une dorsale, les plaques s’écartent et du magma remonte ; en refroidissant, il forme de la nouvelle croûte océanique.",),
    mcq("earth",6,"Que se passe-t-il le plus souvent lorsqu’une plaque océanique converge avec une plaque continentale ?",["La plaque océanique plonge sous la plaque continentale","La plaque continentale disparaît sous l’océanique, toujours","Les deux plaques s’éloignent","Les deux plaques cessent de bouger"],[0],"Plus dense, la lithosphère océanique peut s’enfoncer sous la lithosphère continentale : c’est la subduction."),
    mcq("earth",7,"La collision de deux lithosphères continentales peut former :",["Une chaîne de montagnes","Une nouvelle dorsale océanique","Une fosse au milieu d’un océan uniquement","Une couche de gaz"],[0],"La convergence continentale raccourcit et épaissit la croûte, ce qui peut édifier une chaîne de montagnes."),
    vf("earth",8,"Une limite transformante correspond principalement à un coulissage horizontal entre deux plaques.",True,"Les plaques glissent latéralement l’une contre l’autre ; ce mouvement peut produire des séismes."),
    vf("earth",9,"L’expansion océanique se produit au niveau des dorsales.",True,"La création de croûte à la dorsale éloigne progressivement les fonds océaniques plus anciens."),
    mcq("earth",10,"En moyenne, la lithosphère océanique est :",["Plus dense et plus mince que la lithosphère continentale","Moins dense et beaucoup plus épaisse","Composée uniquement de granite","Toujours plus ancienne que les continents"],[0],"La croûte océanique basaltique est plus dense et généralement plus mince que la croûte continentale."),
    mcq("earth",11,"Quelle roche est fréquemment associée à la croûte océanique ?",["Le basalte","Le calcaire uniquement","Le charbon","Le sel gemme"],[0],"Le basalte est une roche magmatique fréquente en surface de la croûte océanique ; le gabbro se forme en profondeur dans cette croûte."),
    mcq("earth",12,"Le foyer (hypocentre) d’un séisme est :",["Le point en profondeur où débute la rupture","Le point le plus éloigné de la faille","Le sommet d’un volcan","La limite entre le noyau et le manteau"],[0],"La rupture débute au foyer en profondeur ; l’épicentre est le point de surface situé à sa verticale."),
    vf("earth",13,"L’épicentre d’un séisme est le point de la surface situé à la verticale du foyer.",True,"La distinction foyer–épicentre aide à décrire la localisation d’un séisme."),
    mcq("earth",14,"Les ondes sismiques sont :",["Des vibrations qui se propagent depuis le foyer","Des courants océaniques","Des vents dans l’atmosphère","Des couches de roches immobiles"],[0],"Un séisme libère de l’énergie sous forme d’ondes qui se propagent dans la Terre et à sa surface."),
    vf("earth",15,"Les ondes S ne se propagent pas dans les milieux liquides.",True,"Le comportement des ondes S fournit des indices sur les propriétés des matériaux traversés, notamment le noyau externe liquide."),
    mcq("earth",16,"Le magma désigne :",["Un matériau rocheux fondu présent en profondeur","De la lave déjà refroidie","Une roche sédimentaire","De l’eau souterraine"],[0],"Le magma est un mélange de liquide, de cristaux et parfois de gaz en profondeur ; à la surface, on parle de lave."),
    mcq("earth",17,"Une lave fluide, pauvre en silice, donne le plus souvent un volcanisme :",["Effusif, avec des coulées","Explosif uniquement","Sans éruption possible","Lié à une météorite"],[0],"Une lave relativement fluide libère plus facilement ses gaz et s’écoule ; les magmas visqueux retiennent davantage les gaz."),
    vf("earth",18,"Les éruptions explosives sont souvent favorisées par un magma visqueux riche en gaz.",True,"La viscosité freine la libération des gaz, ce qui peut accroître la pression avant l’éruption."),
    mcq("earth",19,"Le refroidissement d’un magma peut former :",["Une roche magmatique","Un fossile directement","Une cellule vivante","Une vague sismique"],[0],"Quand le magma ou la lave refroidit et cristallise, il forme une roche magmatique."),
    vf("earth",20,"Tous les volcans se trouvent exclusivement sur les limites des plaques.",False,"Faux : la majorité est liée aux limites des plaques, mais certains volcans se forment aussi au-dessus de points chauds intraplaques."),
    mcq("earth",21,"Quel est le lien entre l’âge du plancher océanique et la distance à une dorsale ?",["Il est généralement plus ancien quand on s’éloigne de la dorsale","Il est toujours plus jeune loin de la dorsale","Il a le même âge partout","L’âge dépend uniquement de la profondeur"],[0],"La croûte se forme à la dorsale puis s’écarte ; l’âge du plancher augmente donc généralement avec la distance à l’axe."),
    vf("earth",22,"Des bandes magnétiques symétriques de part et d’autre de certaines dorsales soutiennent l’expansion océanique.",True,"Les basaltes enregistrent le champ magnétique au moment de leur refroidissement ; la symétrie des bandes reflète la création bilatérale du plancher."),
    mcq("earth",23,"Quel type d’indice a historiquement soutenu l’idée d’une ancienne réunion des continents ?",["L’emboîtement de certaines côtes et la présence de fossiles similaires sur des continents séparés","La couleur actuelle des océans","La forme des nuages","Les saisons"],[0],"La complémentarité de certains continents et des indices géologiques ou fossiles communs ont soutenu l’hypothèse de la dérive des continents."),
    vf("earth",24,"La distribution de roches et de chaînes géologiques comparables sur des continents séparés peut aider à reconstituer leur histoire.",True,"Des continuités géologiques sont cohérentes avec le déplacement passé des continents."),
    mcq("earth",25,"La chaleur interne de la Terre contribue notamment :",["Aux mouvements lents du manteau et à la dynamique des plaques","À arrêter les séismes","À supprimer la gravité","À créer les marées uniquement"],[0],"La chaleur interne participe aux mouvements de convection du manteau et au fonctionnement de la tectonique, dans un modèle simplifié."),
    mcq("earth",26,"La couche externe solide et relativement mince de la Terre est :",["La croûte","Le noyau interne","Le manteau inférieur","L’atmosphère"],[0],"La croûte est l’enveloppe rocheuse externe ; elle est continentale ou océanique."),
    vf("earth",27,"Le noyau externe terrestre est liquide, tandis que le noyau interne est solide.",True,"Les propriétés des ondes sismiques montrent que le noyau externe est liquide et le noyau interne solide."),
    mcq("earth",28,"Une faille géologique est :",["Une fracture accompagnée d’un déplacement de blocs rocheux","Un type de fossile","Une couche de l’atmosphère","Un minéral dissous dans l’eau"],[0],"Une faille est une cassure le long de laquelle des blocs se sont déplacés ; son activité peut être à l’origine de séismes."),
    vf("earth",29,"Un aléa naturel et un risque sont exactement la même notion.",False,"Faux : l’aléa est la possibilité d’un phénomène ; le risque dépend aussi de l’exposition et de la vulnérabilité des personnes et des biens."),
    mcq("earth",30,"Quel comportement réduit le risque lors d’un séisme ?",["Appliquer les consignes de sécurité et se mettre à l’abri de façon adaptée","Prendre l’ascenseur pendant les secousses","Se placer près des vitres","Ignorer les consignes locales"],[0],"La préparation, les constructions adaptées et le respect des consignes réduisent la vulnérabilité ; on ne peut pas empêcher l’aléa."),
    mcq("earth",31,"Un fossile est :",["Un reste ou une trace d’un organisme ancien conservé dans une roche","Une roche volcanique récente uniquement","Un animal vivant","Une molécule d’ADN intacte dans toute roche"],[0],"Les fossiles comprennent des restes ou des traces d’organismes anciens conservés dans des conditions favorables."),
    vf("earth",32,"La succession des fossiles dans les couches géologiques apporte des indices sur les changements de la vie au cours du temps.",True,"Les fossiles permettent d’étudier l’histoire de la biodiversité et les apparitions ou disparitions d’organismes."),
    mcq("earth",33,"Dans une série de couches sédimentaires non bouleversée, le principe de superposition indique généralement que :",["Les couches inférieures sont plus anciennes que celles qui les recouvrent","Les couches supérieures sont toujours les plus anciennes","Toutes les couches ont le même âge","Les fossiles ne peuvent pas se conserver"],[0],"En l’absence de perturbation, une couche déposée plus tôt se trouve sous les couches déposées ensuite."),
    mcq("earth",34,"Un fossile stratigraphique utile est généralement celui d’une espèce :",["De courte durée d’existence et largement répartie","Qui n’a vécu qu’en un seul petit lieu pendant des millions d’années","Toujours actuelle","Sans caractères reconnaissables"],[0],"Une espèce répandue mais limitée à une période relativement courte aide à comparer l’âge de couches éloignées."),
    mcq("earth",35,"Des structures homologues chez plusieurs espèces indiquent souvent :",["Une origine évolutive commune, même si leur fonction diffère","Une fonction toujours identique","Une absence de parenté","Une apparition simultanée"],[0],"Les structures homologues partagent un plan d’organisation hérité d’un ancêtre commun, même si elles ont évolué vers des fonctions différentes."),
    mcq("earth",36,"Des structures analogues sont des structures qui :",["Ont une fonction proche mais une origine évolutive différente","Ont toujours les mêmes os","Prouvent une parenté directe récente","Sont dépourvues de fonction"],[0],"L’analogie concerne une ressemblance fonctionnelle qui peut résulter d’évolutions indépendantes."),
    vf("earth",37,"Des ressemblances observées au cours du développement embryonnaire peuvent constituer un indice de parenté évolutive.",True,"Des caractères embryonnaires partagés peuvent refléter un héritage commun, à interpréter avec d’autres indices."),
    mcq("earth",38,"La comparaison des séquences d’ADN entre espèces peut aider à :",["Évaluer leur parenté évolutive","Mesurer directement leur taille adulte","Déterminer leur âge sans aucune donnée","Prouver qu’elles vivent dans le même milieu"],[0],"Les ressemblances moléculaires, notamment dans l’ADN, contribuent à reconstruire les liens de parenté."),
    mcq("earth",39,"Pour que la sélection naturelle puisse modifier une population, il faut notamment :",["Des variations héréditaires et des différences de succès reproducteur","Que chaque individu décide de changer","L’absence totale de reproduction","Que le milieu reste toujours identique"],[0],"La sélection agit sur des variations héréditaires lorsque certains phénotypes contribuent davantage à la génération suivante."),
    vf("earth",40,"La sélection naturelle choisit consciemment les caractères dont les individus ont besoin.",False,"Faux : la sélection n’a pas d’intention. Les individus porteurs de variations avantageuses dans un contexte donné peuvent laisser davantage de descendants."),
    vf("earth",41,"Une adaptation évolutive se met en place dans une population au fil des générations, et non parce qu’un individu en a besoin.",True,"Les fréquences des caractères héréditaires changent au fil des générations sous l’effet de la sélection et d’autres mécanismes."),
    mcq("earth",42,"Une mutation de l’ADN peut :",["Créer un nouvel allèle","Garantir un avantage à son porteur","Toujours provoquer une maladie","Faire évoluer immédiatement toute une population"],[0],"Une mutation crée une nouvelle variante génétique ; ses effets peuvent être neutres, défavorables ou avantageux selon le contexte."),
    mcq("earth",43,"L’isolement reproducteur entre populations peut conduire à :",["La formation de nouvelles espèces au cours du temps","La disparition de toutes les mutations","La fusion obligatoire des populations","L’arrêt des générations"],[0],"Lorsque les échanges génétiques deviennent limités et que les populations divergent, une spéciation peut se produire."),
    vf("earth",44,"La spéciation correspond à la formation de nouvelles espèces.",True,"La spéciation résulte d’une divergence évolutive accompagnée d’un isolement reproducteur selon le concept biologique classique."),
    mcq("earth",45,"La dérive génétique a souvent un effet plus marqué :",["Dans une petite population","Dans une population infinie","Uniquement chez les fossiles","Seulement dans les océans"],[0],"Le hasard de la reproduction peut modifier les fréquences alléliques ; son effet est plus fort dans les petites populations."),
    vf("earth",46,"La migration d’individus entre populations peut transférer des allèles d’une population à une autre.",True,"Le flux de gènes relie les populations en transportant des variantes génétiques."),
    mcq("earth",47,"Une population bactérienne devient résistante à un antibiotique principalement parce que :",["Les bactéries résistantes préexistantes survivent et se reproduisent davantage sous traitement","Les bactéries décident de fabriquer la mutation utile","L’antibiotique transforme toutes les bactéries de la même façon","La résistance apparaît toujours chez chaque individu exposé"],[0],"L’antibiotique exerce une pression de sélection : les bactéries déjà résistantes ont un avantage relatif et peuvent devenir plus fréquentes."),
    mcq("earth",48,"Le mélanisme industriel est souvent utilisé comme exemple de :",["Sélection naturelle en réponse à un environnement","Formation immédiate d’un fossile","Dérive des continents","Reproduction sans hérédité"],[0],"Dans certaines populations de papillons, les phénotypes les mieux camouflés dans un environnement donné ont eu un avantage de survie."),
    mcq("earth",49,"La sélection artificielle est réalisée principalement par :",["Les humains qui choisissent quels individus se reproduisent","Les volcans qui déplacent les plaques","Les fossiles qui mutent","Les séismes"],[0],"En sélection artificielle, les humains favorisent volontairement la reproduction d’individus possédant des caractères recherchés."),
    mcq("earth",50,"Dans un arbre de parenté, un nœud représente généralement :",["Un ancêtre commun hypothétique","Un organisme qui vit forcément aujourd’hui","Une mutation unique toujours visible","Une échelle de taille"],[0],"Un nœud correspond à l’ancêtre commun hypothétique des lignées qui en partent."),
    vf("earth",51,"Deux espèces proches sur un arbre de parenté partagent un ancêtre commun plus récent que deux espèces éloignées sur cet arbre.",True,"La proximité se lit à partir du dernier ancêtre commun, et non de la position gauche-droite des noms."),
    vf("earth",52,"Des caractères ressemblants peuvent apparaître indépendamment dans des lignées différentes sous des contraintes similaires.",True,"Cette évolution convergente peut produire des analogies qui ne signalent pas à elles seules une parenté proche."),
    mcq("earth",53,"Un fossile de transition est utile parce qu’il :",["Présente un assemblage de caractères reliant des groupes au cours de leur histoire","Prouve que l’évolution est toujours linéaire","Est nécessairement l’ancêtre direct de toutes les espèces actuelles","N’a aucun caractère identifiable"],[0],"Les formes fossiles présentant des combinaisons de caractères aident à documenter les transformations évolutives, sans être nécessairement des ancêtres directs."),
    vf("earth",54,"L’évolution a pour objectif de rendre les espèces parfaites.",False,"Faux : l’évolution n’a pas de but. Les populations changent selon les variations et les conditions de leur environnement."),
    vf("earth",55,"Les individus d’une population peuvent présenter des variations de caractères.",True,"La variation au sein des populations fournit la matière première de plusieurs mécanismes évolutifs."),
    mcq("earth",56,"Laquelle de ces situations peut augmenter la diversité génétique d’une population ?",["L’apparition de mutations et le brassage lié à la reproduction sexuée","La copie strictement identique de chaque génome sans mutation","L’absence de reproduction pendant des générations","La disparition de tous les allèles"],[0],"Les mutations créent de nouveaux allèles et la reproduction sexuée recombine les variantes déjà présentes."),
    vf("earth",57,"La reproduction sexuée peut produire des descendants génétiquement différents de leurs parents.",True,"La méiose et la fécondation recombinent les allèles et contribuent à la diversité des descendants."),
    mcq("earth",58,"Si l’environnement change, un caractère auparavant avantageux :",["Peut ne plus procurer le même avantage","Devient forcément utile pour toujours","Disparaît immédiatement chez chaque individu","N’est jamais soumis à la sélection"],[0],"L’avantage d’un caractère dépend du contexte ; la sélection naturelle varie donc avec l’environnement."),
    mcq("earth",59,"Quelle phrase décrit le mieux les relations évolutives entre humains et autres primates actuels ?",["Les humains et les autres primates actuels partagent des ancêtres communs","Les humains descendent des singes actuels","Les primates actuels n’ont aucun lien de parenté","Toutes les espèces actuelles sont identiques"],[0],"Les humains et les autres primates actuels appartiennent à des lignées distinctes qui partagent des ancêtres communs dans le passé."),
    vf("earth",60,"La biodiversité actuelle est le résultat d’une histoire comprenant des apparitions, des transformations et des extinctions.",True,"La biodiversité change au cours du temps sous l’effet de l’évolution et des événements qui affectent les populations."),
]

THEMES["nutrition"]["questions"] = THEMES["nutrition"]["provided"]
THEMES["genetics"]["questions"] = THEMES["genetics"]["provided"]
for q in GENETICS: THEMES["genetics"]["questions"].append(q)
THEMES["earth"]["questions"] = EARTH

# Add educational Wikimedia images to a few especially relevant questions. Files are bundled locally.
IMAGES = {
    ("nutrition", 37): {"src":"assets/digestive-system.svg", "alt":"Schéma du système digestif humain", "credit":"Mariana Ruiz (LadyofHats), domaine public, Wikimedia Commons"},
    ("genetics", 9): {"src":"assets/dna-double-helix.jpg", "alt":"Illustration de la double hélice de l’ADN", "credit":"Genomics Education Programme, CC BY 2.0, Wikimedia Commons"},
    ("earth", 5): {"src":"assets/tectonic-plate-boundaries.png", "alt":"Schéma des principaux types de limites entre plaques tectoniques", "credit":"Jose F. Vigil / USGS, domaine public, Wikimedia Commons"},
}
for theme_id, data in THEMES.items():
    # Normalize question ids and enforce theme field for original questions.
    data["questions"].sort(key=lambda q: q["id"])
    for q in data["questions"]:
        q["theme"] = theme_id
        if (theme_id, q["id"]) in IMAGES: q["illustration"] = IMAGES[(theme_id, q["id"])]

expected = {"nutrition": 60, "genetics": 60, "earth": 60}
for name, count in expected.items():
    if len(THEMES[name]["questions"]) != count:
        raise SystemExit(f"{name}: {len(THEMES[name]['questions'])} questions, expected {count}")
    ids = [q["id"] for q in THEMES[name]["questions"]]
    if ids != list(range(1, count+1)): raise SystemExit(f"{name}: non-contiguous ids {ids}")

result = {
    "version": 1,
    "langue": "fr",
    "niveau": "3ème année Sciences expérimentales — Tunisie",
    "total_questions": 180,
    "source_note": "L’annexe fournie s’interrompt après la question 48 du thème Information génétique. Les questions 49–60 de ce thème et les 60 questions du thème Dynamique du globe terrestre et évolution biologique sont des compléments pédagogiques rédigés pour compléter le quiz.",
    "themes": [{"id": key, "titre": val["title"], "questions": val["questions"]} for key, val in THEMES.items()]
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {OUT}: {sum(len(t['questions']) for t in result['themes'])} questions")
