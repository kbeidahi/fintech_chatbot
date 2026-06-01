"""
Multilingual FAQ — Arabic, French, English
"""

MULTILINGUAL_FAQ = [

    # ── BALANCE INQUIRY ──────────────────────────────────────────────────────
    {
        "category": "Balance",
        "question_ar": "كيف أعرف رصيدي؟",
        "question_fr": "Comment consulter mon solde?",
        "question_en": "How do I check my balance?",
        "answer_ar": (
            "لمعرفة رصيدك اتبع الخطوات التالية:\n\n"
            "1️⃣ افتح التطبيق وسجّل الدخول إلى حسابك.\n"
            "2️⃣ في الصفحة الرئيسية اضغط على قسم 'الحسابات' (Accounts) من الشريط العلوي.\n"
            "3️⃣ سيظهر لك رصيدك الحالي مباشرةً مع تفاصيل حسابك.\n\n"
            "💡 يمكنك أيضاً كتابة 'رصيد' في المحادثة لعرض رصيدك فوراً."
        ),
        "answer_fr": (
            "Pour consulter votre solde, suivez ces étapes:\n\n"
            "1️⃣ Ouvrez l'application et connectez-vous à votre compte.\n"
            "2️⃣ Sur la page principale, appuyez sur 'Comptes' dans la barre supérieure.\n"
            "3️⃣ Votre solde actuel s'affichera immédiatement avec les détails de votre compte.\n\n"
            "💡 Vous pouvez aussi taper 'solde' dans le chat pour l'afficher instantanément."
        ),
        "answer_en": (
            "To check your balance, follow these steps:\n\n"
            "1️⃣ Open the app and log in to your account.\n"
            "2️⃣ On the main page, tap 'Accounts' in the top bar.\n"
            "3️⃣ Your current balance will be displayed immediately with your account details.\n\n"
            "💡 You can also type 'balance' in the chat to display it instantly."
        ),
        "keywords_ar": (
            "رصيد,رصيدي,كم رصيدي,اعرض رصيدي,رصيد حسابي,كم عندي,المبلغ المتاح,"
            "كيف اعرف رصيدي,اريد اعرف رصيدي,عرض الرصيد,فين رصيدي,حسابي,كم في حسابي,"
            "ما رصيدي,اطلع على رصيدي,شوف رصيدي,وين رصيدي"
        ),
        "keywords_fr": (
            "solde,mon solde,solde actuel,solde disponible,combien,voir solde,afficher solde,"
            "consulter solde,quel est mon solde,comment voir mon solde,vérifier solde,"
            "connaître mon solde,afficher mon compte,voir mon compte,montant disponible"
        ),
        "keywords_en": (
            "balance,my balance,show balance,check balance,available balance,how much,"
            "see my balance,view balance,account balance,what is my balance,how to check balance,"
            "display balance,know my balance,remaining balance,funds available"
        ),
        "action": "check_balance",
    },

    # ── PHONE TOP-UP ──────────────────────────────────────────────────────────
    {
        "category": "Phone",
        "question_ar": "كيف أشحن رصيد الهاتف؟",
        "question_fr": "Comment recharger mon crédit téléphonique?",
        "question_en": "How do I top up phone credit?",
        "answer_ar": (
            "لشحن رصيد الهاتف اتبع الخطوات التالية:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'شحن الهاتف' (Phone Recharge).\n"
            "2️⃣ اختر شبكة الاتصال:\n"
            "   • موريتل (Mauritel)\n"
            "   • شنقيتل (Chinguitel)\n"
            "   • ماتل (Mattel)\n"
            "3️⃣ أدخل رقم الهاتف المراد شحنه.\n"
            "4️⃣ أدخل المبلغ المطلوب.\n"
            "5️⃣ اضغط على 'إرسال' أو 'تأكيد'.\n"
            "6️⃣ أدخل رقمك السري (PIN) لتأكيد العملية.\n\n"
            "✅ سيتم شحن الرصيد فوراً بعد إدخال الرقم السري."
        ),
        "answer_fr": (
            "Pour recharger un crédit téléphonique, suivez ces étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'Recharge Téléphone'.\n"
            "2️⃣ Choisissez l'opérateur:\n"
            "   • Mauritel\n"
            "   • Chinguitel\n"
            "   • Mattel\n"
            "3️⃣ Entrez le numéro de téléphone à recharger.\n"
            "4️⃣ Entrez le montant souhaité.\n"
            "5️⃣ Appuyez sur 'Envoyer' ou 'Confirmer'.\n"
            "6️⃣ Entrez votre code PIN pour confirmer l'opération.\n\n"
            "✅ La recharge sera effectuée instantanément après la saisie du code PIN."
        ),
        "answer_en": (
            "To top up phone credit, follow these steps:\n\n"
            "1️⃣ On the main page, tap 'Phone Recharge'.\n"
            "2️⃣ Choose your network operator:\n"
            "   • Mauritel\n"
            "   • Chinguitel\n"
            "   • Mattel\n"
            "3️⃣ Enter the phone number to top up.\n"
            "4️⃣ Enter the amount.\n"
            "5️⃣ Tap 'Send' or 'Confirm'.\n"
            "6️⃣ Enter your PIN to confirm the operation.\n\n"
            "✅ The credit will be added instantly after entering your PIN."
        ),
        "keywords_ar": (
            "شحن,شحن هاتف,رصيد هاتف,شحن رقم,اشحن,شحن موبايل,رصيد موبايل,"
            "موريتل,شنقيتل,ماتل,كيف اشحن,طريقة الشحن,شحن الخط,شحن الرقم,"
            "اريد اشحن,بغيت اشحن,شحن رصيد,تعبئة رصيد,تعبئة هاتف"
        ),
        "keywords_fr": (
            "recharge,recharger,crédit téléphonique,recharge mobile,recharge téléphone,"
            "mauritel,chinguitel,mattel,comment recharger,recharger mon téléphone,"
            "recharger un numéro,crédit phone,recharge réseau,comment faire une recharge"
        ),
        "keywords_en": (
            "topup,top up,phone credit,recharge,mobile credit,phone recharge,"
            "mauritel,chinguitel,mattel,how to recharge,recharge phone,top up phone,"
            "add credit,phone balance,mobile recharge,reload phone,credit top up"
        ),
        "action": "phone_topup",
    },

    # ── FUND TRANSFER ─────────────────────────────────────────────────────────
    {
        "category": "Transfer",
        "question_ar": "كيف أحول الأموال؟",
        "question_fr": "Comment faire un virement?",
        "question_en": "How do I transfer money?",
        "answer_ar": (
            "لتحويل الأموال اتبع الخطوات التالية:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'تحويل' (Transfers) من الشريط العلوي.\n"
            "2️⃣ أدخل رقم هاتف المستلم.\n"
            "3️⃣ أدخل المبلغ المراد إرساله.\n"
            "4️⃣ اضغط على 'إرسال'.\n"
            "5️⃣ أدخل رقمك السري (PIN) لتأكيد التحويل.\n\n"
            "✅ سيصل المبلغ فوراً إلى حساب المستلم.\n"
            "⚠️ تأكد من صحة رقم الهاتف قبل الإرسال."
        ),
        "answer_fr": (
            "Pour effectuer un virement, suivez ces étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'Virements' dans la barre supérieure.\n"
            "2️⃣ Entrez le numéro de téléphone du destinataire.\n"
            "3️⃣ Entrez le montant à envoyer.\n"
            "4️⃣ Appuyez sur 'Envoyer'.\n"
            "5️⃣ Entrez votre code PIN pour confirmer le virement.\n\n"
            "✅ Le montant arrivera instantanément sur le compte du destinataire.\n"
            "⚠️ Vérifiez bien le numéro avant d'envoyer."
        ),
        "answer_en": (
            "To transfer money, follow these steps:\n\n"
            "1️⃣ On the main page, tap 'Transfers' in the top bar.\n"
            "2️⃣ Enter the recipient's phone number.\n"
            "3️⃣ Enter the amount to send.\n"
            "4️⃣ Tap 'Send'.\n"
            "5️⃣ Enter your PIN to confirm the transfer.\n\n"
            "✅ The amount will reach the recipient's account instantly.\n"
            "⚠️ Make sure the phone number is correct before sending."
        ),
        "keywords_ar": (
            "تحويل,حول,ارسل,إرسال أموال,تحويل أموال,أرسل مبلغ,حوّل,ارسال,"
            "كيف احول,طريقة التحويل,بعت فلوس,ارسال فلوس,تحويل مبلغ,"
            "اريد احول,بغيت احول,ارسل مبلغ,تحويل لشخص,ارسل لشخص,حول مبلغ"
        ),
        "keywords_fr": (
            "virement,virer,transférer,transfert,envoyer argent,faire virement,envoyer,"
            "comment virer,comment transférer,envoyer de l argent,faire un transfert,"
            "envoyer un virement,transfert d argent,comment envoyer de l argent"
        ),
        "keywords_en": (
            "transfer,send money,wire,send funds,transfer money,send,"
            "how to transfer,how to send money,money transfer,send to someone,"
            "transfer to someone,how do i send,wire transfer,move money"
        ),
        "action": "transfer",
    },

    # ── GIMTEL TRANSFER ───────────────────────────────────────────────────────
    {
        "category": "GIMTEL",
        "question_ar": "كيف أرسل أموال عبر GIMTEL؟",
        "question_fr": "Comment faire un virement GIMTEL?",
        "question_en": "How do I send money via GIMTEL?",
        "answer_ar": (
            "خدمة GIMTEL تتيح لك إرسال الأموال إلى تطبيقات مالية أخرى. اتبع الخطوات:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على أيقونة 'GIMTEL' (الشعار G).\n"
            "2️⃣ أدخل اسم التطبيق المستلم:\n"
            "   • Bankily • Click • Sedad • Bamis\n"
            "   • Gaza Pay • Moov Money • Masrivi\n"
            "3️⃣ أدخل المبلغ المراد إرساله.\n"
            "4️⃣ أدخل رقم هاتف المستلم.\n"
            "5️⃣ أدخل رقمك السري (PIN) لتأكيد العملية.\n\n"
            "✅ سيتم إرسال المبلغ مباشرة إلى التطبيق المحدد."
        ),
        "answer_fr": (
            "Le service GIMTEL vous permet d'envoyer de l'argent vers d'autres applications financières. Étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur l'icône 'GIMTEL' (logo G).\n"
            "2️⃣ Entrez le nom de l'application destinataire:\n"
            "   • Bankily • Click • Sedad • Bamis\n"
            "   • Gaza Pay • Moov Money • Masrivi\n"
            "3️⃣ Entrez le montant à envoyer.\n"
            "4️⃣ Entrez le numéro de téléphone du destinataire.\n"
            "5️⃣ Entrez votre code PIN pour confirmer l'opération.\n\n"
            "✅ Le montant sera transféré directement vers l'application choisie."
        ),
        "answer_en": (
            "GIMTEL lets you send money to other financial apps. Follow these steps:\n\n"
            "1️⃣ On the main page, tap the 'GIMTEL' icon (G logo).\n"
            "2️⃣ Enter the recipient app name:\n"
            "   • Bankily • Click • Sedad • Bamis\n"
            "   • Gaza Pay • Moov Money • Masrivi\n"
            "3️⃣ Enter the amount to send.\n"
            "4️⃣ Enter the recipient's phone number.\n"
            "5️⃣ Enter your PIN to confirm the operation.\n\n"
            "✅ The amount will be sent directly to the selected app."
        ),
        "keywords_ar": (
            "جيمتل,gimtel,بنكيلي,كليك,سيداد,باميس,moov money,مصرفي,"
            "تحويل لتطبيق,ارسل لبنكيلي,ارسل لكليك,تحويل بين التطبيقات,"
            "كيف استخدم جيمتل,خدمة جيمتل,ما هو جيمتل,جيمتال"
        ),
        "keywords_fr": (
            "gimtel,bankily,click,sedad,bamis,moov money,masrivi,"
            "virement gimtel,comment utiliser gimtel,transfert vers application,"
            "envoyer via gimtel,qu est ce que gimtel,service gimtel"
        ),
        "keywords_en": (
            "gimtel,bankily,click,sedad,bamis,moov money,masrivi,"
            "gimtel transfer,how to use gimtel,send via gimtel,transfer to app,"
            "interbank transfer,what is gimtel,gimtel service,send to bankily"
        ),
        "action": "gimtel_transfer",
    },

    # ── BILL PAYMENT ──────────────────────────────────────────────────────────
    {
        "category": "Bills",
        "question_ar": "كيف أدفع الفواتير؟",
        "question_fr": "Comment payer mes factures?",
        "question_en": "How do I pay bills?",
        "answer_ar": (
            "لدفع الفواتير اتبع الخطوات التالية:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'تسديد الفواتير' (Bill Payment).\n"
            "2️⃣ اختر نوع الفاتورة من القائمة:\n"
            "   ⚡ كهرباء | 💧 ماء | 🌐 إنترنت | 📺 تلفزيون (TOD by BeIN / TV)\n"
            "   🛡️ تأمين | 🏦 مالية | 🎓 تعليم | ✈️ نقل جوي | 🏛️ إدارة\n"
            "3️⃣ اختر الشركة المزودة للخدمة.\n"
            "4️⃣ أدخل معرّفك (ID) الخاص بالمؤسسة — ستظهر فاتورتك تلقائياً.\n"
            "5️⃣ أدخل المبلغ المطلوب دفعه.\n"
            "6️⃣ أدخل رقمك السري (PIN) لتأكيد الدفع.\n\n"
            "✅ سيتم تسديد الفاتورة فوراً وستصلك رسالة تأكيد."
        ),
        "answer_fr": (
            "Pour payer vos factures, suivez ces étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'Paiement de Factures'.\n"
            "2️⃣ Choisissez le type de facture dans la liste:\n"
            "   ⚡ Électricité | 💧 Eau | 🌐 Internet | 📺 Télévision (TOD by BeIN)\n"
            "   🛡️ Assurance | 🏦 Finance | 🎓 Éducation | ✈️ Transport aérien | 🏛️ Administration\n"
            "3️⃣ Choisissez le fournisseur de service.\n"
            "4️⃣ Entrez votre identifiant — votre facture apparaîtra automatiquement.\n"
            "5️⃣ Entrez le montant à payer.\n"
            "6️⃣ Entrez votre code PIN pour confirmer le paiement.\n\n"
            "✅ La facture sera réglée instantanément et vous recevrez une confirmation."
        ),
        "answer_en": (
            "To pay bills, follow these steps:\n\n"
            "1️⃣ On the main page, tap 'Bill Payment'.\n"
            "2️⃣ Choose the bill category from the list:\n"
            "   ⚡ Electricity | 💧 Water | 🌐 Internet | 📺 TV (TOD by BeIN / TV)\n"
            "   🛡️ Insurance | 🏦 Finance | 🎓 Education | ✈️ Air Transport | 🏛️ Administration\n"
            "3️⃣ Choose the service provider/company.\n"
            "4️⃣ Enter your ID — your bill will appear automatically.\n"
            "5️⃣ Enter the amount to pay.\n"
            "6️⃣ Enter your PIN to confirm the payment.\n\n"
            "✅ The bill will be paid instantly and you will receive a confirmation."
        ),
        "keywords_ar": (
            "فاتورة,دفع فاتورة,فاتورة كهرباء,فاتورة ماء,فاتورة انترنت,سداد,تسديد,"
            "كهرباء,ماء,انترنت,تلفزيون,تأمين,تعليم,ادارة,نقل جوي,"
            "كيف ادفع فاتورة,طريقة دفع الفاتورة,اريد ادفع فاتورة,دفع الخدمات,"
            "تسديد فاتورة الكهرباء,تسديد فاتورة الماء,دفع فواتير,فاتورتي"
        ),
        "keywords_fr": (
            "facture,payer facture,facture électricité,facture eau,facture internet,règlement,"
            "électricité,eau,internet,télévision,assurance,éducation,administration,transport aérien,"
            "comment payer une facture,régler une facture,paiement facture,payer mes factures,"
            "facture bein,facture tod,tod bein"
        ),
        "keywords_en": (
            "bill,pay bill,electricity bill,water bill,internet bill,payment,"
            "electricity,water,internet,tv,insurance,education,administration,air transport,"
            "how to pay bill,pay my bills,bill payment,settle bill,pay utilities,"
            "bein sports,tod bein,pay electricity,pay water"
        ),
        "action": "bill_payment",
    },

    # ── WITHDRAWAL ────────────────────────────────────────────────────────────
    {
        "category": "Withdrawal",
        "question_ar": "كيف أسحب الأموال؟",
        "question_fr": "Comment retirer de l'argent?",
        "question_en": "How do I withdraw money?",
        "answer_ar": (
            "لسحب الأموال عبر الوكالة اتبع الخطوات التالية:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'Cash Out'.\n"
            "2️⃣ أدخل رقم أو معرّف (ID) أقرب وكالة إليك.\n"
            "3️⃣ أدخل المبلغ المراد سحبه.\n"
            "4️⃣ أدخل رقمك السري (PIN) لتأكيد العملية.\n"
            "5️⃣ ستصلك رسالة تحتوي على كود السحب.\n"
            "6️⃣ أعطِ هذا الكود لصاحب الوكالة وستستلم أموالك نقداً.\n\n"
            "✅ العملية آمنة وفورية.\n"
            "⚠️ لا تشارك الكود مع أي شخص غير صاحب الوكالة."
        ),
        "answer_fr": (
            "Pour retirer de l'argent via une agence, suivez ces étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'Retrait'.\n"
            "2️⃣ Entrez le numéro ou l'identifiant de l'agence la plus proche.\n"
            "3️⃣ Entrez le montant à retirer.\n"
            "4️⃣ Entrez votre code PIN pour confirmer l'opération.\n"
            "5️⃣ Vous recevrez un message contenant un code de retrait.\n"
            "6️⃣ Donnez ce code au gérant de l'agence et vous recevrez votre argent en espèces.\n\n"
            "✅ L'opération est sécurisée et instantanée.\n"
            "⚠️ Ne partagez le code qu'avec le gérant de l'agence."
        ),
        "answer_en": (
            "To withdraw cash via an agency, follow these steps:\n\n"
            "1️⃣ On the main page, tap 'Cash Out'.\n"
            "2️⃣ Enter the number or ID of the nearest agency.\n"
            "3️⃣ Enter the amount to withdraw.\n"
            "4️⃣ Enter your PIN to confirm the operation.\n"
            "5️⃣ You will receive a message with a withdrawal code.\n"
            "6️⃣ Give this code to the agency owner and you will receive your cash.\n\n"
            "✅ The operation is secure and instant.\n"
            "⚠️ Only share the code with the agency owner."
        ),
        "keywords_ar": (
            "سحب,أسحب,سحب نقود,سحب أموال,سحب من حسابي,cash out,كاش اوت,وكالة,"
            "كيف اسحب,طريقة السحب,اريد اسحب فلوس,سحب نقدي,استلام فلوس,"
            "اسحب من وكالة,سحب عبر وكالة,فلوس نقد,نقود,اريد نقود"
        ),
        "keywords_fr": (
            "retrait,retirer,retirer argent,retrait bancaire,espèces,agence,cash out,"
            "comment retirer,faire un retrait,retrait en espèces,retirer de l argent,"
            "retrait via agence,comment retirer de l argent,récupérer argent"
        ),
        "keywords_en": (
            "withdraw,withdrawal,cash,cash out,cashout,agency,take money out,"
            "how to withdraw,get cash,withdraw money,cash withdrawal,get money out,"
            "withdraw from agency,collect cash,how to get cash"
        ),
        "action": "withdrawal",
    },

    # ── B-PAY ─────────────────────────────────────────────────────────────────
    {
        "category": "BPay",
        "question_ar": "كيف أدفع للتجار عبر B-Pay؟",
        "question_fr": "Comment payer les marchands via B-Pay?",
        "question_en": "How do I pay merchants via B-Pay?",
        "answer_ar": (
            "لإتمام الدفع للتجار عبر B-Pay اتبع الخطوات:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'B-Pay'.\n"
            "2️⃣ أدخل معرّف التاجر (Merchant ID).\n"
            "3️⃣ أدخل المبلغ المراد دفعه.\n"
            "4️⃣ أدخل رقمك السري (PIN) لتأكيد الدفع.\n\n"
            "✅ سيتم الدفع فوراً وسيستلم التاجر المبلغ مباشرة."
        ),
        "answer_fr": (
            "Pour payer un commerçant via B-Pay, suivez ces étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'B-Pay'.\n"
            "2️⃣ Entrez l'identifiant du commerçant.\n"
            "3️⃣ Entrez le montant à payer.\n"
            "4️⃣ Entrez votre code PIN pour confirmer le paiement.\n\n"
            "✅ Le paiement sera effectué instantanément."
        ),
        "answer_en": (
            "To pay a merchant via B-Pay, follow these steps:\n\n"
            "1️⃣ On the main page, tap 'B-Pay'.\n"
            "2️⃣ Enter the Merchant ID.\n"
            "3️⃣ Enter the amount to pay.\n"
            "4️⃣ Enter your PIN to confirm the payment.\n\n"
            "✅ The payment will be processed instantly."
        ),
        "keywords_ar": (
            "b-pay,بي باي,دفع للتاجر,دفع بالمتجر,تاجر,معرف التاجر,"
            "كيف استخدم b-pay,طريقة الدفع للتاجر,دفع في المحل,دفع للمحل,"
            "ما هو b-pay,خدمة b-pay,الدفع الالكتروني للتاجر"
        ),
        "keywords_fr": (
            "b-pay,bpay,paiement marchand,payer commerçant,marchand,identifiant marchand,"
            "comment utiliser b-pay,payer en magasin,paiement en point de vente,"
            "qu est ce que b-pay,service b-pay,payer chez un commerçant"
        ),
        "keywords_en": (
            "b-pay,bpay,merchant payment,pay merchant,merchant id,store payment,b pay,"
            "how to use b-pay,pay at store,pay shop,what is b-pay,"
            "b-pay service,pay a merchant,merchant,shop payment"
        ),
        "action": None,
    },

    # ── TAX / FEES ────────────────────────────────────────────────────────────
    {
        "category": "Fees",
        "question_ar": "ما هي الرسوم المطبقة؟",
        "question_fr": "Quels sont les frais appliqués?",
        "question_en": "What are the applied fees?",
        "answer_ar": (
            "الرسوم المطبقة على العمليات:\n\n"
            "• 💸 تحويل الأموال: 0.5%\n"
            "• 💵 سحب النقود: 0.3%\n"
            "• 🧾 دفع الفواتير: مجاني\n"
            "• 📱 شحن الهاتف: مجاني\n"
            "• 🏪 B-Pay: مجاني\n\n"
            "للمزيد من المعلومات تواصل مع خدمة العملاء."
        ),
        "answer_fr": (
            "Frais appliqués sur les opérations:\n\n"
            "• 💸 Virement: 0.5%\n"
            "• 💵 Retrait: 0.3%\n"
            "• 🧾 Paiement de factures: gratuit\n"
            "• 📱 Recharge téléphone: gratuit\n"
            "• 🏪 B-Pay: gratuit\n\n"
            "Pour plus d'informations, contactez le service client."
        ),
        "answer_en": (
            "Fees applied on operations:\n\n"
            "• 💸 Money transfer: 0.5%\n"
            "• 💵 Cash withdrawal: 0.3%\n"
            "• 🧾 Bill payments: free\n"
            "• 📱 Phone top-up: free\n"
            "• 🏪 B-Pay: free\n\n"
            "For more information contact customer service."
        ),
        "keywords_ar": (
            "ضريبة,ضرائب,رسوم,اقتطاعات,رسوم بنكية,تكلفة,كم الرسوم,"
            "هل هناك رسوم,رسوم التحويل,رسوم السحب,مجاني,بكام الرسوم"
        ),
        "keywords_fr": (
            "taxe,taxes,frais,commissions,frais bancaires,coût,gratuit,"
            "y a-t-il des frais,frais de virement,frais de retrait,combien coute"
        ),
        "keywords_en": (
            "tax,taxes,fees,charges,bank fees,cost,commission,free,"
            "are there fees,transfer fees,withdrawal fees,how much does it cost"
        ),
        "action": None,
    },

    # ── CHEQUE BOOK ───────────────────────────────────────────────────────────
    {
        "category": "Cheque",
        "question_ar": "كيف أطلب دفتر شيكات؟",
        "question_fr": "Comment demander un carnet de chèques?",
        "question_en": "How do I request a cheque book?",
        "answer_ar": (
            "لطلب دفتر شيكات اتبع الخطوات التالية:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'Request Cheque Book'.\n"
            "2️⃣ أدخل بياناتك وعنوان التوصيل.\n"
            "3️⃣ أكّد الطلب برقمك السري (PIN).\n\n"
            "✅ سيتم إرسال دفتر الشيكات إليك خلال 5-7 أيام عمل.\n"
            "بدلاً من ذلك يمكنك زيارة أقرب فرع لاستلامه مباشرة."
        ),
        "answer_fr": (
            "Pour demander un carnet de chèques, suivez ces étapes:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'Demande de Chéquier'.\n"
            "2️⃣ Entrez vos informations et votre adresse de livraison.\n"
            "3️⃣ Confirmez la demande avec votre code PIN.\n\n"
            "✅ Le carnet de chèques vous sera envoyé sous 5 à 7 jours ouvrables.\n"
            "Vous pouvez aussi visiter l'agence la plus proche pour le récupérer directement."
        ),
        "answer_en": (
            "To request a cheque book, follow these steps:\n\n"
            "1️⃣ On the main page, tap 'Request Cheque Book'.\n"
            "2️⃣ Enter your details and delivery address.\n"
            "3️⃣ Confirm the request with your PIN.\n\n"
            "✅ The cheque book will be sent to you within 5-7 business days.\n"
            "You can also visit the nearest branch to collect it directly."
        ),
        "keywords_ar": (
            "شيك,دفتر شيكات,شيكات,طلب شيكات,دفتر الشيك,"
            "كيف اطلب شيكات,اريد دفتر شيكات,cheque book,cheque"
        ),
        "keywords_fr": (
            "chèque,carnet de chèques,chéquier,demander chèques,"
            "comment demander un chéquier,cheque book"
        ),
        "keywords_en": (
            "cheque,cheque book,checkbook,check book,request cheque,"
            "how to get cheque book,order cheque book"
        ),
        "action": None,
    },

    # ── CARD MANAGEMENT ───────────────────────────────────────────────────────
    {
        "category": "Card",
        "question_ar": "كيف أحصل على بطاقة مصرفية؟",
        "question_fr": "Comment obtenir une carte bancaire?",
        "question_en": "How do I get a debit card?",
        "answer_ar": (
            "للحصول على بطاقة مصرفية:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على 'Debit Card'.\n"
            "2️⃣ اختر 'طلب بطاقة جديدة'.\n"
            "3️⃣ أدخل بياناتك وعنوان التوصيل.\n"
            "4️⃣ أكّد الطلب برقمك السري (PIN).\n\n"
            "✅ ستصلك البطاقة خلال 5-7 أيام عمل.\n"
            "بدلاً من ذلك يمكنك زيارة أقرب فرع لاستلامها مباشرة."
        ),
        "answer_fr": (
            "Pour obtenir une carte bancaire:\n\n"
            "1️⃣ Sur la page principale, appuyez sur 'Carte de Débit'.\n"
            "2️⃣ Choisissez 'Demander une nouvelle carte'.\n"
            "3️⃣ Entrez vos informations et votre adresse de livraison.\n"
            "4️⃣ Confirmez la demande avec votre code PIN.\n\n"
            "✅ Vous recevrez la carte sous 5 à 7 jours ouvrables.\n"
            "Vous pouvez aussi visiter l'agence la plus proche pour la récupérer directement."
        ),
        "answer_en": (
            "To get a debit card:\n\n"
            "1️⃣ On the main page, tap 'Debit Card'.\n"
            "2️⃣ Select 'Request a new card'.\n"
            "3️⃣ Enter your details and delivery address.\n"
            "4️⃣ Confirm the request with your PIN.\n\n"
            "✅ The card will be delivered within 5-7 business days.\n"
            "Alternatively, you can visit the nearest branch to collect it directly."
        ),
        "keywords_ar": (
            "بطاقة,بطاقة مصرفية,بطاقة صراف,فيزا,طلب بطاقة,بطاقة بنكية,كارت,debit card,"
            "كيف احصل على بطاقة,اريد بطاقة,طلب كارت,بطاقة ائتمان,بطاقة دفع"
        ),
        "keywords_fr": (
            "carte,carte bancaire,carte débit,visa,demander carte,carte de paiement,debit card,"
            "comment obtenir une carte,je veux une carte,demander une carte bancaire"
        ),
        "keywords_en": (
            "card,debit card,get card,request card,bank card,visa,new card,card services,"
            "how to get a card,i want a card,order card,apply for card"
        ),
        "action": None,
    },

    # ── PIN MANAGEMENT ────────────────────────────────────────────────────────
    {
        "category": "PIN",
        "question_ar": "كيف أغير أو استرجع رقمي السري؟",
        "question_fr": "Comment changer ou récupérer mon code PIN?",
        "question_en": "How do I change or recover my PIN?",
        "answer_ar": (
            "لإدارة رقمك السري:\n\n"
            "🔄 لتغيير الرقم السري:\n"
            "1️⃣ اذهب إلى الإعدادات ← الأمان ← تغيير الرقم السري.\n"
            "2️⃣ أدخل الرقم القديم ثم الرقم الجديد مرتين.\n\n"
            "❓ إذا نسيت رقمك السري:\n"
            "1️⃣ في شاشة إدخال الرقم السري اضغط على 'نسيت الرقم السري'.\n"
            "2️⃣ ستصلك رسالة SMS تحتوي على كود إعادة التعيين.\n"
            "3️⃣ أدخل الكود وأنشئ رقماً سرياً جديداً.\n\n"
            "⚠️ لا تشارك رقمك السري مع أي شخص."
        ),
        "answer_fr": (
            "Pour gérer votre code PIN:\n\n"
            "🔄 Pour changer le code PIN:\n"
            "1️⃣ Allez dans Paramètres → Sécurité → Modifier le code PIN.\n"
            "2️⃣ Entrez l'ancien code, puis le nouveau deux fois.\n\n"
            "❓ Si vous avez oublié votre code PIN:\n"
            "1️⃣ Sur l'écran de saisie, appuyez sur 'Code PIN oublié'.\n"
            "2️⃣ Vous recevrez un SMS avec un code de réinitialisation.\n"
            "3️⃣ Entrez le code et créez un nouveau code PIN.\n\n"
            "⚠️ Ne partagez jamais votre code PIN avec quiconque."
        ),
        "answer_en": (
            "To manage your PIN:\n\n"
            "🔄 To change PIN:\n"
            "1️⃣ Go to Settings → Security → Change PIN.\n"
            "2️⃣ Enter the old PIN then the new one twice.\n\n"
            "❓ If you forgot your PIN:\n"
            "1️⃣ On the PIN screen, tap 'Forgot PIN'.\n"
            "2️⃣ You will receive an SMS with a reset code.\n"
            "3️⃣ Enter the code and create a new PIN.\n\n"
            "⚠️ Never share your PIN with anyone."
        ),
        "keywords_ar": (
            "رقم سري,pin,كلمة سر,نسيت رقمي,تغيير الرقم,رقم المرور,كود,"
            "نسيت,كيف اغير رقمي السري,نسيت الرقم السري,استرجاع الرقم السري,"
            "تغيير pin,ريست pin,رقم سري جديد,ما رقمي السري"
        ),
        "keywords_fr": (
            "pin,code pin,mot de passe,oublié pin,changer pin,code secret,réinitialiser,"
            "j ai oublié mon pin,comment changer mon pin,récupérer pin,"
            "réinitialiser pin,nouveau pin,mot de passe oublié"
        ),
        "keywords_en": (
            "pin,my pin,forgot pin,change pin,reset pin,pin code,secret code,lost pin,"
            "how to change pin,i forgot my pin,recover pin,new pin,pin management"
        ),
        "action": None,
    },

    # ── TRANSACTION HISTORY ───────────────────────────────────────────────────
    {
        "category": "Transactions",
        "question_ar": "كيف أعرض سجل معاملاتي؟",
        "question_fr": "Comment voir mon historique de transactions?",
        "question_en": "How do I view my transaction history?",
        "answer_ar": (
            "لعرض سجل معاملاتك:\n\n"
            "1️⃣ في الصفحة الرئيسية اضغط على أيقونة السجل 🕐 في الشريط العلوي.\n"
            "2️⃣ ستظهر لك قائمة بجميع عملياتك السابقة:\n"
            "   • التحويلات\n"
            "   • شحن الهاتف\n"
            "   • دفع الفواتير\n"
            "   • السحب النقدي\n"
            "3️⃣ اضغط على أي معاملة لعرض تفاصيلها."
        ),
        "answer_fr": (
            "Pour voir votre historique de transactions:\n\n"
            "1️⃣ Sur la page principale, appuyez sur l'icône historique 🕐 dans la barre supérieure.\n"
            "2️⃣ La liste de toutes vos opérations passées s'affichera:\n"
            "   • Virements\n"
            "   • Recharges téléphoniques\n"
            "   • Paiements de factures\n"
            "   • Retraits en espèces\n"
            "3️⃣ Appuyez sur une opération pour en voir les détails."
        ),
        "answer_en": (
            "To view your transaction history:\n\n"
            "1️⃣ On the main page, tap the history icon 🕐 in the top bar.\n"
            "2️⃣ A list of all your past operations will appear:\n"
            "   • Transfers\n"
            "   • Phone top-ups\n"
            "   • Bill payments\n"
            "   • Cash withdrawals\n"
            "3️⃣ Tap any transaction to view its details."
        ),
        "keywords_ar": (
            "معاملات,سجل المعاملات,تاريخ العمليات,عملياتي,السجل,العمليات السابقة,"
            "كيف اشوف معاملاتي,شوف عملياتي,سجل العمليات,تاريخ المعاملات,"
            "عمليات سابقة,اريد اشوف معاملاتي,كشف الحساب"
        ),
        "keywords_fr": (
            "transactions,historique,historique transactions,mes transactions,opérations,relevé,"
            "voir mes transactions,comment voir mes transactions,historique des opérations,"
            "mes opérations,relevé de compte"
        ),
        "keywords_en": (
            "transactions,transaction history,history,my transactions,show transactions,"
            "past transactions,statement,operations,recent transactions,"
            "how to see transactions,view my transactions,account statement"
        ),
        "action": None,
    },

    # ── GREETING / HELP ───────────────────────────────────────────────────────
    {
        "category": "Greeting",
        "question_ar": "مرحبا",
        "question_fr": "Bonjour",
        "question_en": "Hello",
        "answer_ar": (
            "مرحباً! أنا مساعدك المالي الذكي في FinAssist 👋\n\n"
            "يمكنني مساعدتك في:\n"
            "💰 معرفة رصيدك\n"
            "📱 شحن رصيد الهاتف (موريتل، شنقيتل، ماتل)\n"
            "💸 تحويل الأموال\n"
            "🔄 التحويل عبر GIMTEL\n"
            "🧾 دفع الفواتير (كهرباء، ماء، إنترنت...)\n"
            "💵 سحب النقود عبر الوكالة\n"
            "🏪 الدفع للتجار عبر B-Pay\n"
            "📒 طلب دفتر شيكات\n"
            "💳 خدمات البطاقة المصرفية\n"
            "🔑 إدارة الرقم السري\n\n"
            "كيف يمكنني مساعدتك اليوم؟"
        ),
        "answer_fr": (
            "Bonjour! Je suis votre assistant financier intelligent FinAssist 👋\n\n"
            "Je peux vous aider avec:\n"
            "💰 Consulter votre solde\n"
            "📱 Recharger votre téléphone (Mauritel, Chinguitel, Mattel)\n"
            "💸 Faire des virements\n"
            "🔄 Virements GIMTEL\n"
            "🧾 Payer vos factures (Électricité, Eau, Internet...)\n"
            "💵 Retrait d'espèces via agence\n"
            "🏪 Paiement marchand via B-Pay\n"
            "📒 Demande de carnet de chèques\n"
            "💳 Services carte bancaire\n"
            "🔑 Gestion du code PIN\n\n"
            "Comment puis-je vous aider aujourd'hui?"
        ),
        "answer_en": (
            "Hello! I'm your smart financial assistant FinAssist 👋\n\n"
            "I can help you with:\n"
            "💰 Check your balance\n"
            "📱 Phone top-up (Mauritel, Chinguitel, Mattel)\n"
            "💸 Money transfers\n"
            "🔄 GIMTEL transfers\n"
            "🧾 Bill payments (Electricity, Water, Internet...)\n"
            "💵 Cash withdrawal via agency\n"
            "🏪 Merchant payments via B-Pay\n"
            "📒 Request cheque book\n"
            "💳 Debit card services\n"
            "🔑 PIN management\n\n"
            "How can I help you today?"
        ),
        "keywords_ar": (
            "مرحبا,السلام عليكم,هلا,اهلا,صباح الخير,مساء الخير,كيف حالك,"
            "مساعدة,ماذا تفعل,ما هي خدماتك,ما الذي يمكنك فعله,ابدا,ابدأ,"
            "اهلا وسهلا,مرحبتين,هلا والله,السلام,وعليكم السلام"
        ),
        "keywords_fr": (
            "bonjour,salut,bonsoir,hello,hi,comment allez vous,bonne journée,"
            "aide,help,que pouvez vous faire,vos services,comment utiliser,"
            "bonne matinée,bonne soirée,coucou,commencer"
        ),
        "keywords_en": (
            "hello,hi,hey,how are you,good morning,good afternoon,good evening,"
            "help,what can you do,services,what services,assist,assistance,start,"
            "good day,howdy,greetings,what do you offer,how can you help"
        ),
        "action": None,
    },
]
