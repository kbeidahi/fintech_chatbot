"""
Multilingual FAQ — Arabic, French, English
Based on the provided service document.
"""

MULTILINGUAL_FAQ = [

    # ── BALANCE INQUIRY ──────────────────────────────────────────────────────
    {
        "category": "Balance",
        "question_ar": "ما هو رصيدي البنكي؟",
        "question_fr": "Quel est mon solde bancaire?",
        "question_en": "What is my bank balance?",
        "answer_ar": "يمكنك الاطلاع على رصيدك من خلال الأمر 'رصيد' أو 'اعرض رصيدي'. سيتم عرض رصيدك الحالي فوراً.",
        "answer_fr": "Vous pouvez consulter votre solde en tapant 'solde' ou 'mon solde'. Votre solde actuel sera affiché immédiatement.",
        "answer_en": "You can check your balance by typing 'balance' or 'show balance'. Your current balance will be displayed immediately.",
        "keywords_ar": "رصيد,رصيدي,كم رصيدي,اعرض رصيدي,رصيد حسابي,كم عندي,المبلغ المتاح",
        "keywords_fr": "solde,mon solde,solde actuel,solde disponible,combien,voir solde,afficher solde",
        "keywords_en": "balance,my balance,show balance,check balance,available balance,how much",
        "action": "check_balance",
    },

    # ── TAX INFORMATION ───────────────────────────────────────────────────────
    {
        "category": "Tax",
        "question_ar": "ما هي الضرائب المطبقة؟",
        "question_fr": "Quelles sont les taxes appliquées?",
        "question_en": "What are the applied taxes?",
        "answer_ar": "تطبق البنك رسوم ضريبية على بعض العمليات: تحويل الأموال 0.5%، سحب النقود 0.3%، دفع الفواتير معفى من الضرائب. للمزيد تواصل مع خدمة العملاء.",
        "answer_fr": "La banque applique des frais fiscaux sur certaines opérations: virement 0.5%, retrait 0.3%, paiement de factures exonéré. Pour plus d'informations, contactez le service client.",
        "answer_en": "The bank applies tax fees on some operations: transfers 0.5%, withdrawals 0.3%, bill payments are tax-exempt. For more info contact customer service.",
        "keywords_ar": "ضريبة,ضرائب,رسوم,اقتطاعات,ضريبة بنكية,الضرائب على العمليات",
        "keywords_fr": "taxe,taxes,impôts,frais fiscaux,prélèvements fiscaux,fiscalité bancaire",
        "keywords_en": "tax,taxes,fees,fiscal,bank charges,tax on operations",
        "action": None,
    },

    # ── FUND TRANSFER ─────────────────────────────────────────────────────────
    {
        "category": "Transfer",
        "question_ar": "كيف أحول الأموال؟",
        "question_fr": "Comment faire un virement?",
        "question_en": "How do I transfer money?",
        "answer_ar": "لتحويل الأموال اكتب: 'حول [المبلغ] إلى [اسم المستخدم]'. مثال: 'حول 500 إلى ahmed'. التحويل فوري ومجاني.",
        "answer_fr": "Pour faire un virement tapez: 'virer [montant] à [nom utilisateur]'. Exemple: 'virer 500 à ahmed'. Le virement est instantané et gratuit.",
        "answer_en": "To transfer money type: 'transfer [amount] to [username]'. Example: 'transfer 500 to ahmed'. Transfers are instant and free.",
        "keywords_ar": "تحويل,حول,ارسل,إرسال أموال,تحويل أموال,أرسل مبلغ,حوّل",
        "keywords_fr": "virement,virer,transférer,transfert,envoyer argent,faire virement",
        "keywords_en": "transfer,send money,wire,send funds,transfer money",
        "action": "transfer",
    },

    # ── PHONE TOP-UP ──────────────────────────────────────────────────────────
    {
        "category": "Phone",
        "question_ar": "كيف أشحن رصيد الهاتف؟",
        "question_fr": "Comment recharger mon crédit téléphonique?",
        "question_en": "How do I top up phone credit?",
        "answer_ar": "لشحن رصيد الهاتف اكتب: 'شحن [رقم الهاتف] بمبلغ [المبلغ]'. مثال: 'شحن 22334455 بمبلغ 100'. يمكنك شحن أي رقم هاتف.",
        "answer_fr": "Pour recharger tapez: 'recharge [numéro] montant [montant]'. Exemple: 'recharge 22334455 montant 100'. Vous pouvez recharger n'importe quel numéro.",
        "answer_en": "To top up type: 'topup [phone number] amount [amount]'. Example: 'topup 22334455 amount 100'. You can top up any phone number.",
        "keywords_ar": "شحن,شحن هاتف,رصيد هاتف,شحن رقم,اشحن,شحن موبايل,رصيد موبايل",
        "keywords_fr": "recharge,recharger,crédit téléphonique,recharge mobile,recharge téléphone",
        "keywords_en": "topup,top up,phone credit,recharge,mobile credit,phone recharge",
        "action": "phone_topup",
    },

    # ── BILL PAYMENT ──────────────────────────────────────────────────────────
    {
        "category": "Bills",
        "question_ar": "كيف أدفع الفواتير؟",
        "question_fr": "Comment payer mes factures?",
        "question_en": "How do I pay bills?",
        "answer_ar": "لدفع الفاتورة اكتب: 'دفع فاتورة [نوع الفاتورة] بمبلغ [المبلغ]'. أنواع الفواتير: كهرباء، ماء، إنترنت. مثال: 'دفع فاتورة كهرباء 500'.",
        "answer_fr": "Pour payer une facture tapez: 'payer facture [type] montant [montant]'. Types: électricité, eau, internet. Exemple: 'payer facture électricité 500'.",
        "answer_en": "To pay a bill type: 'pay bill [type] amount [amount]'. Types: electricity, water, internet. Example: 'pay bill electricity 500'.",
        "keywords_ar": "فاتورة,دفع فاتورة,فاتورة كهرباء,فاتورة ماء,فاتورة انترنت,سداد,دفع",
        "keywords_fr": "facture,payer facture,facture électricité,facture eau,facture internet,règlement",
        "keywords_en": "bill,pay bill,electricity bill,water bill,internet bill,payment",
        "action": "bill_payment",
    },

    # ── WITHDRAWAL ────────────────────────────────────────────────────────────
    {
        "category": "Withdrawal",
        "question_ar": "كيف أسحب الأموال؟",
        "question_fr": "Comment retirer de l'argent?",
        "question_en": "How do I withdraw money?",
        "answer_ar": "لسحب الأموال اكتب: 'سحب [المبلغ]'. مثال: 'سحب 1000'. يمكنك السحب من أي صراف آلي باستخدام بطاقتك.",
        "answer_fr": "Pour retirer tapez: 'retrait [montant]'. Exemple: 'retrait 1000'. Vous pouvez retirer dans n'importe quel distributeur avec votre carte.",
        "answer_en": "To withdraw type: 'withdraw [amount]'. Example: 'withdraw 1000'. You can withdraw from any ATM using your card.",
        "keywords_ar": "سحب,أسحب,سحب نقود,سحب أموال,سحب من حسابي,اريد اسحب",
        "keywords_fr": "retrait,retirer,retirer argent,retrait bancaire,espèces,distributeur",
        "keywords_en": "withdraw,withdrawal,cash,atm withdrawal,take money out",
        "action": "withdrawal",
    },

    # ── GIMTEL TRANSFER ───────────────────────────────────────────────────────
    {
        "category": "GIMTEL",
        "question_ar": "كيف أرسل أموال عبر GIMTEL؟",
        "question_fr": "Comment faire un virement GIMTEL?",
        "question_en": "How do I send money via GIMTEL?",
        "answer_ar": "لتحويل عبر GIMTEL اكتب: 'جيمتل [اسم التطبيق] [المبلغ]'. التطبيقات المدعومة: بنكيلي، كليك، سيداد، باميس، Gaza Pay، Moov Money، مصرفي. مثال: 'جيمتل بنكيلي 500'.",
        "answer_fr": "Pour un virement GIMTEL tapez: 'gimtel [nom application] [montant]'. Applications supportées: Bankily, Click, Sedad, Bamis, Gaza Pay, Moov Money, Masrivi. Exemple: 'gimtel bankily 500'.",
        "answer_en": "For GIMTEL transfer type: 'gimtel [app name] [amount]'. Supported apps: Bankily, Click, Sedad, Bamis, Gaza Pay, Moov Money, Masrivi. Example: 'gimtel bankily 500'.",
        "keywords_ar": "جيمتل,بنكيلي,كليك,سيداد,باميس,gaza pay,moov money,مصرفي,تحويل بنكي,تحويل لبنك آخر",
        "keywords_fr": "gimtel,bankily,click,sedad,bamis,gaza pay,moov money,masrivi,virement interbancaire",
        "keywords_en": "gimtel,bankily,click,sedad,bamis,gaza pay,moov money,masrivi,interbank transfer",
        "action": "gimtel_transfer",
    },

    # ── PURCHASE PAYMENT ──────────────────────────────────────────────────────
    {
        "category": "Purchase",
        "question_ar": "كيف أدفع مشترياتي؟",
        "question_fr": "Comment payer mes achats?",
        "question_en": "How do I pay for purchases?",
        "answer_ar": "لدفع مشترياتك اكتب: 'شراء [وصف] بمبلغ [المبلغ]'. مثال: 'شراء سوبرماركت بمبلغ 2000'. يمكن أيضاً الدفع عبر QR Code في المتاجر.",
        "answer_fr": "Pour payer vos achats tapez: 'achat [description] montant [montant]'. Exemple: 'achat supermarché montant 2000'. Vous pouvez aussi payer via QR Code en magasin.",
        "answer_en": "To pay for purchases type: 'purchase [description] amount [amount]'. Example: 'purchase supermarket amount 2000'. You can also pay via QR Code in stores.",
        "keywords_ar": "شراء,دفع مشتريات,دفع بالحساب,شراء من متجر,دفع للتاجر,اشتري",
        "keywords_fr": "achat,payer achats,paiement achat,acheter,payer commerçant,marchand",
        "keywords_en": "purchase,pay purchase,buy,payment,merchant payment,shopping",
        "action": "purchase",
    },

    # ── GREETING ──────────────────────────────────────────────────────────────
    {
        "category": "Greeting",
        "question_ar": "مرحبا",
        "question_fr": "Bonjour",
        "question_en": "Hello",
        "answer_ar": "مرحباً! أنا مساعدك المالي الذكي. يمكنني مساعدتك في:\n• الاطلاع على رصيدك\n• تحويل الأموال\n• شحن رصيد الهاتف\n• دفع الفواتير\n• السحب النقدي\n• التحويلات عبر GIMTEL\n\nكيف يمكنني مساعدتك اليوم؟",
        "answer_fr": "Bonjour! Je suis votre assistant financier intelligent. Je peux vous aider avec:\n• Consulter votre solde\n• Faire des virements\n• Recharger votre téléphone\n• Payer vos factures\n• Effectuer des retraits\n• Virements GIMTEL\n\nComment puis-je vous aider aujourd'hui?",
        "answer_en": "Hello! I am your smart financial assistant. I can help you with:\n• Check your balance\n• Transfer money\n• Top up phone credit\n• Pay bills\n• Cash withdrawal\n• GIMTEL transfers\n\nHow can I help you today?",
        "keywords_ar": "مرحبا,السلام عليكم,هلا,اهلا,صباح الخير,مساء الخير,كيف حالك",
        "keywords_fr": "bonjour,salut,bonsoir,hello,hi,comment allez vous,bonne journée",
        "keywords_en": "hello,hi,hey,good morning,good afternoon,good evening",
        "action": None,
    },
]
