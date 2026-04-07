# Domain Configuration
#
# This file contains all business-domain settings for your LightRAG deployment.
# Each client fills this out based on their document domain (legal, medical, financial, etc.).
#
# For domain templates, see SETUP.md Step 4b.

## Language

- Summary Language: Hebrew

## Extraction

- Entity Types: ["Person","Organization","Location","ContractParty","LegalClause","Obligation","Deadline","Court","Statute","LegalTerm","Monetary"]

## Extraction Examples

~~~
<Entity_types>
[{entity_types}]

<Input Text>
```
הסכם שכירות זה נערך ונחתם ביום 15.03.2024 בתל אביב, בין חברת אלפא נדל"ן בע"מ (להלן: "המשכיר") לבין מר דוד כהן, ת.ז. 012345678 (להלן: "השוכר").

המשכיר מתחייב להעמיד לרשות השוכר את הנכס ברחוב הרצל 45, תל אביב, לתקופה של 36 חודשים החל מיום 01.05.2024. דמי השכירות החודשיים יעמדו על סך של 12,000 ש"ח בתוספת מע"מ, וישולמו עד ליום החמישי בכל חודש.

במידה והשוכר יפגר בתשלום דמי השכירות למעלה מ-30 יום, יחויב בריבית פיגורים בשיעור של 1.5% לחודש. כל סכסוך הנובע מהסכם זה יידון בבית משפט השלום בתל אביב בלבד, בהתאם לחוק השכירות והשאילה, התשל"א-1971.
```

<Output>
entity{tuple_delimiter}אלפא נדל"ן בע"מ{tuple_delimiter}contractparty{tuple_delimiter}אלפא נדל"ן בע"מ היא חברה המשמשת כמשכיר בהסכם השכירות.
entity{tuple_delimiter}דוד כהן{tuple_delimiter}contractparty{tuple_delimiter}דוד כהן הוא השוכר בהסכם השכירות, בעל ת.ז. 012345678.
entity{tuple_delimiter}רחוב הרצל 45, תל אביב{tuple_delimiter}location{tuple_delimiter}רחוב הרצל 45, תל אביב הוא מיקום הנכס המושכר בהסכם.
entity{tuple_delimiter}תל אביב{tuple_delimiter}location{tuple_delimiter}תל אביב היא העיר בה נחתם ההסכם ובה מצוי הנכס המושכר.
entity{tuple_delimiter}תקופת השכירות{tuple_delimiter}deadline{tuple_delimiter}תקופת השכירות היא 36 חודשים, החל מיום 01.05.2024.
entity{tuple_delimiter}12,000 ש"ח{tuple_delimiter}monetary{tuple_delimiter}דמי השכירות החודשיים עומדים על 12,000 ש"ח בתוספת מע"מ.
entity{tuple_delimiter}תשלום עד ליום החמישי בחודש{tuple_delimiter}obligation{tuple_delimiter}השוכר מחויב לשלם את דמי השכירות עד ליום החמישי בכל חודש.
entity{tuple_delimiter}ריבית פיגורים 1.5%{tuple_delimiter}legalclause{tuple_delimiter}סעיף ריבית הפיגורים קובע חיוב של 1.5% לחודש במקרה של פיגור בתשלום העולה על 30 יום.
entity{tuple_delimiter}בית משפט השלום בתל אביב{tuple_delimiter}court{tuple_delimiter}בית משפט השלום בתל אביב הוא הערכאה המוסמכת לדון בסכסוכים הנובעים מההסכם.
entity{tuple_delimiter}חוק השכירות והשאילה, התשל"א-1971{tuple_delimiter}statute{tuple_delimiter}חוק השכירות והשאילה, התשל"א-1971 הוא הדין החל על ההסכם.
relation{tuple_delimiter}אלפא נדל"ן בע"מ{tuple_delimiter}דוד כהן{tuple_delimiter}יחסי שכירות, התחייבות חוזית{tuple_delimiter}אלפא נדל"ן בע"מ משכירה את הנכס לדוד כהן על פי תנאי ההסכם.
relation{tuple_delimiter}דוד כהן{tuple_delimiter}12,000 ש"ח{tuple_delimiter}חובת תשלום, דמי שכירות{tuple_delimiter}דוד כהן מחויב לשלם דמי שכירות חודשיים בסך 12,000 ש"ח.
relation{tuple_delimiter}דוד כהן{tuple_delimiter}תשלום עד ליום החמישי בחודש{tuple_delimiter}חובת תשלום, לוח זמנים{tuple_delimiter}דוד כהן מחויב לשלם את דמי השכירות עד ליום החמישי בכל חודש.
relation{tuple_delimiter}ריבית פיגורים 1.5%{tuple_delimiter}דוד כהן{tuple_delimiter}סנקציה, פיגור בתשלום{tuple_delimiter}סעיף ריבית הפיגורים חל על דוד כהן במקרה של פיגור בתשלום מעל 30 יום.
relation{tuple_delimiter}בית משפט השלום בתל אביב{tuple_delimiter}חוק השכירות והשאילה, התשל"א-1971{tuple_delimiter}סמכות שיפוט, דין חל{tuple_delimiter}בית משפט השלום בתל אביב ידון בסכסוכים מההסכם בהתאם לחוק השכירות והשאילה.
{completion_delimiter}
~~~

~~~
<Entity_types>
[{entity_types}]

<Input Text>
```
בית המשפט המחוזי בירושלים
ת"א 45678-09-23
כבוד השופטת רחל לוי

המבקשת: חברת גמא טכנולוגיות בע"מ
המשיבה: עיריית ירושלים

החלטה

לאחר עיון בבקשה לצו מניעה זמני ובתשובת המשיבה, ולאחר שמיעת טענות הצדדים בדיון שנערך ביום 20.11.2023, מחליט בית המשפט כדלקמן:

המבקשת טוענת כי המשיבה ביטלה שלא כדין את מכרז 2023/156 לאספקת מערכות מידע, בניגוד לתקנות חובת המכרזים, התשנ"ג-1993. סכום המכרז עמד על 5,200,000 ש"ח.

לאחר בחינת הראיות, בית המשפט מקבל את הבקשה באופן חלקי. ניתן בזה צו מניעה זמני האוסר על המשיבה להתקשר עם צד שלישי כלשהו עד למתן החלטה בהליך העיקרי. המשיבה תישא בהוצאות המבקשת בסך 15,000 ש"ח.
```

<Output>
entity{tuple_delimiter}בית המשפט המחוזי בירושלים{tuple_delimiter}court{tuple_delimiter}בית המשפט המחוזי בירושלים הוא הערכאה השיפוטית הדנה בתיק ת"א 45678-09-23.
entity{tuple_delimiter}רחל לוי{tuple_delimiter}person{tuple_delimiter}השופטת רחל לוי היא השופטת היושבת בדין בתיק ומחליטה בבקשה לצו מניעה זמני.
entity{tuple_delimiter}גמא טכנולוגיות בע"מ{tuple_delimiter}contractparty{tuple_delimiter}גמא טכנולוגיות בע"מ היא המבקשת בהליך, הטוענת לביטול שלא כדין של מכרז.
entity{tuple_delimiter}עיריית ירושלים{tuple_delimiter}contractparty{tuple_delimiter}עיריית ירושלים היא המשיבה בהליך, שביטלה את המכרז.
entity{tuple_delimiter}מכרז 2023/156{tuple_delimiter}legalclause{tuple_delimiter}מכרז 2023/156 הוא מכרז לאספקת מערכות מידע שבוטל על ידי עיריית ירושלים.
entity{tuple_delimiter}5,200,000 ש"ח{tuple_delimiter}monetary{tuple_delimiter}סכום המכרז עמד על 5,200,000 ש"ח.
entity{tuple_delimiter}צו מניעה זמני{tuple_delimiter}legalterm{tuple_delimiter}צו מניעה זמני הוא סעד זמני האוסר על המשיבה להתקשר עם צד שלישי עד להחלטה בהליך העיקרי.
entity{tuple_delimiter}תקנות חובת המכרזים, התשנ"ג-1993{tuple_delimiter}statute{tuple_delimiter}תקנות חובת המכרזים, התשנ"ג-1993 הן הדין שלטענת המבקשת הופר בביטול המכרז.
entity{tuple_delimiter}15,000 ש"ח{tuple_delimiter}monetary{tuple_delimiter}סכום ההוצאות שנפסק לטובת המבקשת עומד על 15,000 ש"ח.
relation{tuple_delimiter}גמא טכנולוגיות בע"מ{tuple_delimiter}עיריית ירושלים{tuple_delimiter}סכסוך משפטי, ביטול מכרז{tuple_delimiter}גמא טכנולוגיות בע"מ תובעת את עיריית ירושלים בגין ביטול שלא כדין של מכרז 2023/156.
relation{tuple_delimiter}עיריית ירושלים{tuple_delimiter}מכרז 2023/156{tuple_delimiter}ביטול, החלטה מנהלית{tuple_delimiter}עיריית ירושלים ביטלה את מכרז 2023/156 לאספקת מערכות מידע.
relation{tuple_delimiter}בית המשפט המחוזי בירושלים{tuple_delimiter}צו מניעה זמני{tuple_delimiter}סעד שיפוטי, החלטה{tuple_delimiter}בית המשפט המחוזי בירושלים נתן צו מניעה זמני חלקי בהליך.
relation{tuple_delimiter}מכרז 2023/156{tuple_delimiter}תקנות חובת המכרזים, התשנ"ג-1993{tuple_delimiter}הפרה נטענת, דין חל{tuple_delimiter}לטענת המבקשת, ביטול המכרז נעשה בניגוד לתקנות חובת המכרזים.
relation{tuple_delimiter}עיריית ירושלים{tuple_delimiter}15,000 ש"ח{tuple_delimiter}הוצאות משפט, חיוב{tuple_delimiter}עיריית ירושלים חויבה בהוצאות המבקשת בסך 15,000 ש"ח.
{completion_delimiter}
~~~

~~~
<Entity_types>
[{entity_types}]

<Input Text>
```
כתב תביעה

התובע: יוסף אברהמי, ת.ז. 987654321, רחוב ויצמן 12, חיפה
הנתבעת: חברת דלתא ביטוח בע"מ

בית המשפט השלום בחיפה מתבקש לחייב את הנתבעת לשלם לתובע פיצויים בסך 280,000 ש"ח בגין דחיית תביעת ביטוח שלא כדין.

עובדות התביעה: ביום 10.06.2023 ארע לתובע אירוע ביטוחי המכוסה על פי פוליסת ביטוח מקיף מספר 7891011. התובע הגיש תביעה כנדרש תוך 30 יום מיום האירוע. הנתבעת דחתה את התביעה ביום 15.08.2023 בטענת כוח עליון, ללא ביסוס עובדתי מספק.

התובע טוען כי הדחייה מנוגדת לסעיף 28 לחוק חוזה הביטוח, התשמ"א-1981, הקובע כי על המבטח לפעול בתום לב ולנמק את דחיית התביעה באופן מפורט.
```

<Output>
entity{tuple_delimiter}יוסף אברהמי{tuple_delimiter}contractparty{tuple_delimiter}יוסף אברהמי הוא התובע בהליך, מבוטח שתביעת הביטוח שלו נדחתה, מתגורר ברחוב ויצמן 12, חיפה.
entity{tuple_delimiter}דלתא ביטוח בע"מ{tuple_delimiter}contractparty{tuple_delimiter}דלתא ביטוח בע"מ היא הנתבעת, חברת הביטוח שדחתה את תביעת המבוטח.
entity{tuple_delimiter}בית המשפט השלום בחיפה{tuple_delimiter}court{tuple_delimiter}בית המשפט השלום בחיפה הוא הערכאה אליה הוגש כתב התביעה.
entity{tuple_delimiter}חיפה{tuple_delimiter}location{tuple_delimiter}חיפה היא עיר מגוריו של התובע ומיקום בית המשפט.
entity{tuple_delimiter}280,000 ש"ח{tuple_delimiter}monetary{tuple_delimiter}סכום הפיצויים הנתבע עומד על 280,000 ש"ח בגין דחיית תביעת ביטוח שלא כדין.
entity{tuple_delimiter}פוליסת ביטוח מקיף 7891011{tuple_delimiter}legalclause{tuple_delimiter}פוליסת ביטוח מקיף מספר 7891011 היא הפוליסה שמכוחה הגיש התובע את תביעת הביטוח.
entity{tuple_delimiter}הגשת תביעה תוך 30 יום{tuple_delimiter}obligation{tuple_delimiter}התובע מילא את חובתו להגיש תביעה תוך 30 יום מיום האירוע הביטוחי.
entity{tuple_delimiter}דחיית התביעה{tuple_delimiter}deadline{tuple_delimiter}הנתבעת דחתה את תביעת הביטוח ביום 15.08.2023.
entity{tuple_delimiter}כוח עליון{tuple_delimiter}legalterm{tuple_delimiter}כוח עליון הוא הטענה המשפטית שבגינה דחתה הנתבעת את תביעת הביטוח, ללא ביסוס עובדתי מספק.
entity{tuple_delimiter}סעיף 28 לחוק חוזה הביטוח, התשמ"א-1981{tuple_delimiter}statute{tuple_delimiter}סעיף 28 לחוק חוזה הביטוח, התשמ"א-1981 קובע כי על המבטח לפעול בתום לב ולנמק דחיית תביעה באופן מפורט.
relation{tuple_delimiter}יוסף אברהמי{tuple_delimiter}דלתא ביטוח בע"מ{tuple_delimiter}תביעת פיצויים, סכסוך ביטוחי{tuple_delimiter}יוסף אברהמי תובע את דלתא ביטוח בע"מ בגין דחיית תביעת ביטוח שלא כדין.
relation{tuple_delimiter}יוסף אברהמי{tuple_delimiter}פוליסת ביטוח מקיף 7891011{tuple_delimiter}מבוטח, זכויות ביטוח{tuple_delimiter}יוסף אברהמי הוא המבוטח על פי פוליסה מספר 7891011.
relation{tuple_delimiter}דלתא ביטוח בע"מ{tuple_delimiter}כוח עליון{tuple_delimiter}טענת הגנה, עילת דחייה{tuple_delimiter}דלתא ביטוח בע"מ דחתה את התביעה בטענת כוח עליון ללא ביסוס מספק.
relation{tuple_delimiter}דלתא ביטוח בע"מ{tuple_delimiter}סעיף 28 לחוק חוזה הביטוח, התשמ"א-1981{tuple_delimiter}הפרה נטענת, חובת תום לב{tuple_delimiter}לטענת התובע, דחיית התביעה מנוגדת לסעיף 28 לחוק חוזה הביטוח המחייב נימוק מפורט.
relation{tuple_delimiter}יוסף אברהמי{tuple_delimiter}280,000 ש"ח{tuple_delimiter}סעד כספי, פיצויים{tuple_delimiter}יוסף אברהמי תובע פיצויים בסך 280,000 ש"ח.
{completion_delimiter}
~~~

## User Prompt

You are answering questions about legal documents. Accuracy is paramount.
If uncertain about any detail, say so explicitly.
Never paraphrase legal clauses — quote them directly.
Always cite the specific document and section when possible.
