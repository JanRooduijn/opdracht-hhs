## Setup
Voer de onderstaande stappen uit. Klik 'Yes' bij elke pop-up.
- Navigeer naar https://github.com/github/codespaces-codeql.
- Klik rechtsboven op 'use this template' en dan op 'open in a codespace'.
- Wacht een tijdje...
- Navigeer in de verticale menubar aan de linkerkant van het scherm naar 'QL'.
- Onder Databases, klik op 'From GitHub'.
- Vul de volgende url in: https://github.com/JanRooduijn/opdracht-hhs.
- Nadat de database is toegevoegd, klik er met de rechter muisknop op, en kies 'Add Database Source to Workspace'.

## Opdracht 1: handmatige analyse
In de Explorer (bovenaan de verticale menubalk aan de linkerkant van het scherm) kan je de broncode van `app.py` nu vinden onder `[JanRooduijn/opdracht-hhs source archive] -> home -> app.py`. Probeer zo veel mogelijk plekken te vinden waar deze Python webapplicatie kwetsbaar is voor SQL-injectie. 

## Opracht 2: CodeQL


1. Vind alle plekken waar een methode wordt uitgevoerd.
    <details>
    <summary>Hint</summary>

    - Het type van een Python methode in CodeQL is `Call`.

    </details>
    <details>
    <summary>Oplossing</summary>

    ```ql
    import python

    from Call c 
    select c
    ```
    </details>

1. De bovenstaande code geeft wel heel veel aanroepen van methoden! Dat komt doordat CodeQL ook door alle Python code zoekt waar `app.py` afhankelijk van is. Maak gebruik van de CodeQL methoden `getLocation()`, `getFile()`, en `getBaseName()` om de zoekresultaten te beperken tot het bestand `app.py`. 
    <details>
    <summary>Hint</summary>

    - De juiste volgorde van het aanroepen van de genoemde methoden is `c.getLocation().getFile().getBaseName()`.

    </details>
    <details>
    <summary>Hint</summary>

    - Om je te beperken tot bepaalde calls kan je de `where` clausule gebruiken.

    </details>
    <details>
    <summary>Oplossing</summary>


    ```ql
    import python

    from Call c 
    where c.getLocation().getFile().getBaseName() = "app.py"
    select c
    ```
    </details>

1. Veel van de calls zijn attributen (herkenbaar aan het feit dat ze rechts van een punt staan). Net als `Call` is `Attribute` ook een type in CodeQL. Breidt de QL-code uit zodat alleen aangeroepen methoden worden gevonden die attributen zijn.
    <details>
    <summary>Hint</summary>

    - Het is niet de call `c` zelf die een attribuut is, maar de functie die door deze call wordt aangeroepen. Die functie kan je vinden door middel van `c.getFunc()`.

    </details>
    <details>
    <summary>Oplossing</summary>

    ```ql
    import python

    from Call c, Attribute a

    where c.getLocation().getFile().getBaseName() = "app.py"
    and c.getFunc() = a
    select c
    ```
    </details>

1. Beperk de query verder zodat alleen de uitgevoerde methodes worden gevonden waar het attribuut `execute` is. 
    <details>
    <summary>Hint</summary>

    - Gebruik de methode `getName()` van de `Attribute` class.
    </details>
    <details>
    <summary>Oplossing</summary>

    ```ql
    import python

    from Call c, Attribute a

    where c.getLocation().getFile().getBaseName() = "app.py"
    and c.getFunc() = a
    and a.getName() = "execute"
    select c, a.getName()
    ```
    </details>

1. Alleen het eerste argument van de `execute` is kwetsbaarvoor SQL-injectie. Verfijn de query zodat telkens het eerste argument wordt gevonden. 

    <details>
    <summary>Hint</summary>

    - De methode `Call.getArg(int i)` geeft het argument met index `i`. 
    </details>
    <details>
    <summary>Oplossing</summary>

    ```ql
   import python

    from Call c, Attribute a
    where c.getLocation().getFile().getBaseName() = "app.py"
    and c.getFunc() = a
    and a.getName() = "execute"
    select a.getName(), c.getArg(0)

    ```
    </details>

 1. In CodeQL is het mogelijk om _predicates_ te maken om je code beter te structureren. Vorm je vorige query om tot een _predicate_ die alle expressies identificeert die worden uitgevoerd als SQL-query. Je kan het volgende template gebruiken:
    ```ql
    predicate isExecutedAsSQL(Expr arg) {
      exists(Call c, Attribute a |
        // TODO vul mij in
      )
    }
    ```
    <details>
    <summary>Hint</summary>

    - Kopieer alles onder `where` in de vorige query
    </details>
    <details>
    <summary>Oplossing</summary>

    ```ql
    import python
    predicate isExecutedAsSQL(Expr arg) {
        exists(Call c, Attribute a |
            c.getLocation().getFile().getBaseName() = "app.py"
            and c.getFunc() = a
            and a.getName() = "execute"
            and arg = c.getArg(0)
        )
    }    
    ```
    </details>

1. Maak een tweede `predicate` dat alle expressies selecteert die user input dragen via de methode `request.json.get`

    <details>
    <summary>Hint</summary>

    - Gebruik de vorige query, maar selecteer nu de hele call in plaats van slechts het eerste argument.
    </details>
    <details>
    <summary>Oplossing</summary>

    ```ql
    predicate isUserInput(Expr arg) {
        exists(Call c, Attribute a |
            c.getLocation().getFile().getBaseName() = "app.py"
            and c.getFunc() = a
            and a.getName() = "get"
            and arg = c
        )
    }
    ```
    </details>

1. Vul, met behulp van de tot nu toe ontwikkelde code, het volgende template in om een volledige DataFlow query te krijgen. 
    ```ql
    import python
    import semmle.python.dataflow.new.DataFlow
    import semmle.python.dataflow.new.TaintTracking

    predicate isExecutedAsSQL(Expr arg) {
        // TODO vul mij in
    }

    predicate isUserInput(Expr arg) {
        // TODO vul mij in
    }

    module SimpleSQLConfig implements DataFlow::ConfigSig {
        predicate isSource(DataFlow::Node source) {
            // TODO vul mij in 
        }

        predicate isSink(DataFlow::Node sink) {
            // TODO vul mij in
        }
    }

    module SimpleSQLFlow = TaintTracking::Global<SimpleSQLConfig>;

    from DataFlow::Node source, DataFlow::Node sink
    where SimpleSQLFlow::flow(source, sink)
    select sink, "This SQL query depends on a $@.", source, "user-provided value"
    ```
    <details>
    <summary>Hint</summary>

    - Gebruik `Node.asExpr()`
    </details>
    
    <details>
    <summary>Oplossing</summary>

    ```ql
    import python
    import semmle.python.dataflow.new.DataFlow
    import semmle.python.dataflow.new.TaintTracking

    predicate isExecutedAsSQL(Expr arg) {
        exists(Call c, Attribute a |
            c.getLocation().getFile().getBaseName() = "app.py"
            and c.getFunc() = a
            and a.getName() = "execute"
            and arg = c.getArg(0)
        )
    }

    predicate isUserInput(Expr arg) {
        exists(Call c, Attribute a |
            c.getLocation().getFile().getBaseName() = "app.py"
            and c.getFunc() = a
            and a.getName() = "get"
            and arg = c
        )
    }

    module SimpleSQLConfig implements DataFlow::ConfigSig {
        predicate isSource(DataFlow::Node source) {
            isUserInput(source.asExpr())
        }

        predicate isSink(DataFlow::Node sink) {
            isExecutedAsSQL(sink.asExpr())
        }
    }

    module SimpleSQLFlow = TaintTracking::Global<SimpleSQLConfig>;

    from DataFlow::Node source, DataFlow::Node sink
    where SimpleSQLFlow::flow(source, sink)
    select sink, "This SQL query depends on a $@.", source, "user-provided value"
    ```
    </details>

1. Je bent pas net begonnen, dus de query die je hebt geschreven is nog niet perfect. Welke _false negatives_ en welke _false positives_ zou jouw query kunnen geven?
    <details>
    <summary>Oplossing</summary>

    - Je vindt nu alle `execute` statements, in plaats van slechts diegene die gedefinieerd worden in `django.db`.
    - Vergelijkbaar: je vindt nu alle `get` statements, in plaats van alleen de `json.get` statements die gedefinieerd worden in `request`.
    - Je neemt in de user input alleen de informatie mee die komt van `get` statements, en niet de parameters van die volgen uit `app.route`.
    - ...
    </details>

1. Draai tot slot de officiële query van CodeQL om SQL-injecties te herknnen in python code: https://github.com/github/codeql/blob/main/python/ql/src/Security/CWE-089/SqlInjection.ql. Vergelijk de uitkomst met de SQL-injectie kwetsbaarheden die jij het gevonden bij de eerste vraag. 



## Bronnen
Deze opdracht is gebaseerd op eerdere tutorials van het CodeQL team van Github. Zie bijvoorbeeld:
- https://github.com/GitHubSecurityLab/codeql-zero-to-hero/tree/main
- https://github.com/githubsatelliteworkshops/codeql/blob/master/java.md
