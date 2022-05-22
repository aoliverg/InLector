# InLector
Scripts for the creation of bilingual ebooks.


To create a blilingual docbook from a docbook, using a MTUOC MT system:

```python3 docbook2bildocbook.py --ip 192.168.1.45 --port 8006 --type MTUOC -i the_adventures_of_sherlock_holmes-eng.docbook -o the_adventures_of_sherlock_holmes-eng-spa.docbook -p MTUOC```

Once created the bilingual docbook, an epub can be created:

```dbtoepub the_adventures_of_sherlock_holmes-eng-spa.docbook -c stylesheet.css```

And to create an html:

```xsltproc -o the_adventures_of_sherlock_holmes-eng-spa.html /usr/share/xml/docbook/stylesheet/docbook-xsl/xhtml-1_1/docbook.xsl the_adventures_of_sherlock_holmes-eng-spa.docbook```

To change the link decoration to none and black, copy in the head section:

```
<style type="text/css">
a {color:#000000; text-decoration:none}
</style>
```
