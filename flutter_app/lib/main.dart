import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'services/api_service.dart';
void main() => runApp(const FinAssistApp());

// ── Colors ────────────────────────────────────────────────────────────────────
class C {
  static const navy    = Color(0xFF0A0E27);
  static const navyL   = Color(0xFF131729);
  static const gold    = Color(0xFFD4A853);
  static const goldL   = Color(0xFFE8C47A);
  static const mint    = Color(0xFF00D4AA);
  static const surface = Color(0xFF1A1F3A);
  static const surfL   = Color(0xFF242B4D);
  static const text    = Color(0xFFF0F2FF);
  static const muted   = Color(0xFF8B93B8);
  static const error   = Color(0xFFFF6B6B);
  static const botBub  = Color(0xFF1E2545);
}

// ── Translations ──────────────────────────────────────────────────────────────
class T {
  static final _d = {
    'en': {
      'appName':'FinAssist','tagline':'Your Smart Financial Guide',
      'login':'Sign In','register':'Create Account','welcome':'Welcome back',
      'username':'Username','email':'Email Address','phone':'Phone (optional)',
      'password':'Password','confirm':'Confirm Password',
      'forgot':'Forgot password?','noAccount':"Don't have an account?",
      'hasAccount':'Already have an account?','hint':'Ask me anything...',
      'newChat':'New Chat','history':'History','suggestions':'Quick Questions',
      'noHistory':'No conversations yet','startChat':'Start chatting',
      'logout':'Logout','messages':'messages','today':'Today','yesterday':'Yesterday',
    },
    'ar': {
      'appName':'فين أسيست','tagline':'مرشدك المالي الذكي',
      'login':'تسجيل الدخول','register':'إنشاء حساب','welcome':'مرحباً بعودتك',
      'username':'اسم المستخدم','email':'البريد الإلكتروني','phone':'الهاتف (اختياري)',
      'password':'كلمة المرور','confirm':'تأكيد كلمة المرور',
      'forgot':'نسيت كلمة المرور؟','noAccount':'ليس لديك حساب؟',
      'hasAccount':'لديك حساب بالفعل؟','hint':'اسألني أي شيء...',
      'newChat':'محادثة جديدة','history':'السجل','suggestions':'أسئلة سريعة',
      'noHistory':'لا توجد محادثات','startChat':'ابدأ محادثة',
      'logout':'تسجيل الخروج','messages':'رسائل','today':'اليوم','yesterday':'أمس',
    },
    'fr': {
      'appName':'FinAssist','tagline':'Votre Guide Financier Intelligent',
      'login':'Se Connecter','register':'Créer un Compte','welcome':'Bon retour',
      'username':"Nom d'utilisateur",'email':'Adresse Email','phone':'Téléphone (optionnel)',
      'password':'Mot de passe','confirm':'Confirmer',
      'forgot':'Mot de passe oublié?','noAccount':'Pas de compte?',
      'hasAccount':'Déjà un compte?','hint':'Posez-moi une question...',
      'newChat':'Nouveau Chat','history':'Historique','suggestions':'Questions Rapides',
      'noHistory':'Aucune conversation','startChat':'Commencer',
      'logout':'Déconnexion','messages':'messages','today':"Aujourd'hui",'yesterday':'Hier',
    },
  };
  static String get(String lang, String key) => _d[lang]?[key] ?? _d['en']![key] ?? key;
}

// ══════════════════════════════════════════════════════════════════════════════
// FAQ ENGINE — كل الأسئلة والأجوبة هنا
// ══════════════════════════════════════════════════════════════════════════════
class FAQ {
  static const _items = [

    // ── 1. رصيد الحساب ────────────────────────────────────────────────────────
    {
      'kw_en': ['balance', 'account balance', 'check balance', 'my balance', 'how much', 'funds'],
      'kw_ar': ['رصيد', 'رصيدي', 'حسابي', 'كم رصيدي', 'اعرف رصيدي', 'الرصيد', 'معرفة الرصيد'],
      'kw_fr': ['solde', 'mon solde', 'vérifier solde', 'consulter solde', 'combien'],
      'a_en': '💰 To check your account balance:\n\n'
          '1. Open the app\n'
          '2. On the Home screen tap your Account\n'
          '3. Your balance will appear immediately\n\n'
          '✅ Your balance updates in real-time with every transaction.',
      'a_ar': '💰 لمعرفة رصيد حسابك:\n\n'
          '1️⃣ افتح التطبيق\n'
          '2️⃣ في الصفحة الرئيسية اضغط على حسابك\n'
          '3️⃣ سيظهر رصيدك مباشرة\n\n'
          '✅ يتحدث رصيدك تلقائياً مع كل معاملة.',
      'a_fr': '💰 Pour consulter votre solde:\n\n'
          '1️⃣ Ouvrez l\'application\n'
          '2️⃣ Sur la page d\'accueil, appuyez sur votre Compte\n'
          '3️⃣ Votre solde s\'affiche immédiatement\n\n'
          '✅ Votre solde se met à jour en temps réel.',
    },

    // ── 2. شحن الهاتف ─────────────────────────────────────────────────────────
    {
      'kw_en': ['phone recharge', 'top up', 'mobile recharge', 'phone credit', 'recharge', 'mauritel', 'chinguitel', 'mattel'],
      'kw_ar': ['شحن', 'شحن هاتف', 'شحن رصيد', 'شحن موبايل', 'موريتل', 'شنقيتل', 'ماتل', 'اشحن'],
      'kw_fr': ['recharge', 'recharger', 'crédit téléphone', 'recharge mobile', 'mauritel', 'chinguitel', 'mattel'],
      'a_en': '📱 To recharge your phone:\n\n'
          '1️⃣ On the Home screen tap "Phone recharge"\n'
          '2️⃣ Choose your network:\n'
          '   • Mauritel\n'
          '   • Chinguitel\n'
          '   • Mattel\n'
          '3️⃣ Enter the phone number\n'
          '4️⃣ Enter the amount\n'
          '5️⃣ Select the service (calls / data)\n'
          '6️⃣ Enter your secret PIN to confirm\n\n'
          '✅ Recharge is instant!',
      'a_ar': '📱 لشحن رصيد الهاتف:\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على "شحن الهاتف"\n'
          '2️⃣ اختر الشبكة:\n'
          '   • موريتل\n'
          '   • شنقيتل\n'
          '   • ماتل\n'
          '3️⃣ أدخل رقم الهاتف\n'
          '4️⃣ أدخل المبلغ\n'
          '5️⃣ اختر الخدمة (مكالمات / إنترنت)\n'
          '6️⃣ أدخل رقمك السري للتأكيد\n\n'
          '✅ الشحن يتم فوراً!',
      'a_fr': '📱 Pour recharger votre téléphone:\n\n'
          '1️⃣ Sur l\'accueil appuyez "Recharge téléphone"\n'
          '2️⃣ Choisissez votre réseau:\n'
          '   • Mauritel\n'
          '   • Chinguitel\n'
          '   • Mattel\n'
          '3️⃣ Entrez le numéro de téléphone\n'
          '4️⃣ Entrez le montant\n'
          '5️⃣ Sélectionnez le service (appels / data)\n'
          '6️⃣ Entrez votre code PIN pour confirmer\n\n'
          '✅ La recharge est instantanée!',
    },

    // ── 3. تحويل الأموال ──────────────────────────────────────────────────────
    {
      'kw_en': ['transfer', 'send money', 'wire', 'send funds', 'transfer money', 'send to'],
      'kw_ar': ['تحويل', 'إرسال', 'أرسل مال', 'حول', 'تحويل أموال', 'إرسال أموال', 'ارسل'],
      'kw_fr': ['virement', 'envoyer argent', 'transférer', 'transfert', 'envoyer'],
      'a_en': '💸 To transfer money:\n\n'
          '1️⃣ On the Home screen tap "Transfers"\n'
          '2️⃣ Enter the recipient\'s phone number\n'
          '3️⃣ Enter the amount to send\n'
          '4️⃣ Tap "Send"\n'
          '5️⃣ Enter your secret PIN to confirm\n\n'
          '✅ Transfer is instant between accounts!\n'
          '⚠️ Double-check the number before confirming.',
      'a_ar': '💸 لتحويل الأموال:\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على "تحويل"\n'
          '2️⃣ أدخل رقم هاتف المستلم\n'
          '3️⃣ أدخل المبلغ المراد إرساله\n'
          '4️⃣ اضغط "إرسال"\n'
          '5️⃣ أدخل رقمك السري للتأكيد\n\n'
          '✅ التحويل يتم فوراً بين الحسابات!\n'
          '⚠️ تأكد من رقم المستلم قبل التأكيد.',
      'a_fr': '💸 Pour transférer de l\'argent:\n\n'
          '1️⃣ Sur l\'accueil appuyez "Transferts"\n'
          '2️⃣ Entrez le numéro de téléphone du destinataire\n'
          '3️⃣ Entrez le montant à envoyer\n'
          '4️⃣ Appuyez "Envoyer"\n'
          '5️⃣ Entrez votre code PIN pour confirmer\n\n'
          '✅ Transfert instantané entre comptes!\n'
          '⚠️ Vérifiez bien le numéro avant de confirmer.',
    },

    // ── 4. جيمتل GIMTEL ───────────────────────────────────────────────────────
    {
      'kw_en': ['gimtel', 'gimtel transfer', 'send to app', 'interbank', 'bankily', 'click', 'sedad', 'masrivi', 'moov', 'bamis'],
      'kw_ar': ['جيمتل', 'gimtel', 'إرسال لتطبيق', 'بنكيلي', 'كليك', 'سيداد', 'مصرفي', 'موف', 'باميس', 'تطبيق آخر', 'تحويل لتطبيق'],
      'kw_fr': ['gimtel', 'virement interbancaire', 'autre application', 'bankily', 'click', 'sedad', 'masrivi'],
      'a_en': '🔄 To send money via GIMTEL to another app:\n\n'
          '1️⃣ On the Home screen tap the "G" GIMTEL icon\n'
          '2️⃣ Enter the name of the target app\n'
          '   (Bankily, Click, Sedad, Masrivi, Moov Money, Bamis...)\n'
          '3️⃣ Enter the recipient\'s phone number\n'
          '4️⃣ Enter the amount to send\n'
          '5️⃣ Enter your secret PIN to confirm\n\n'
          '✅ Money transferred to the other app instantly!',
      'a_ar': '🔄 لإرسال المال عبر خدمة GIMTEL لتطبيق آخر:\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على أيقونة "G" جيمتل\n'
          '2️⃣ أدخل اسم التطبيق المستلم:\n'
          '   (بنكيلي، كليك، سيداد، مصرفي، موف موني، باميس...)\n'
          '3️⃣ أدخل رقم هاتف المستلم\n'
          '4️⃣ أدخل المبلغ المراد إرساله\n'
          '5️⃣ أدخل رقمك السري للتأكيد\n\n'
          '✅ يتم تحويل المال للتطبيق الآخر فوراً!',
      'a_fr': '🔄 Pour envoyer via GIMTEL vers une autre app:\n\n'
          '1️⃣ Sur l\'accueil appuyez l\'icône "G" GIMTEL\n'
          '2️⃣ Entrez le nom de l\'application destinataire:\n'
          '   (Bankily, Click, Sedad, Masrivi, Moov Money, Bamis...)\n'
          '3️⃣ Entrez le numéro de téléphone du destinataire\n'
          '4️⃣ Entrez le montant à envoyer\n'
          '5️⃣ Entrez votre code PIN pour confirmer\n\n'
          '✅ Argent transféré vers l\'autre app instantanément!',
    },

    // ── 5. دفع الفواتير ───────────────────────────────────────────────────────
    {
      'kw_en': ['bill', 'pay bill', 'bills', 'electricity', 'water', 'internet', 'insurance', 'education', 'tv', 'air transport', 'administration', 'finance'],
      'kw_ar': ['فاتورة', 'دفع فاتورة', 'فواتير', 'كهرباء', 'ماء', 'انترنت', 'تأمين', 'تعليم', 'تلفزيون', 'نقل جوي', 'إدارة', 'تسديد'],
      'kw_fr': ['facture', 'payer facture', 'électricité', 'eau', 'internet', 'assurance', 'éducation', 'télévision', 'transport aérien'],
      'a_en': '🧾 To pay your bills:\n\n'
          '1️⃣ On the Home screen tap "Bill Payment"\n'
          '2️⃣ Choose the bill category:\n'
          '   ⚡ Electricity\n'
          '   💧 Water\n'
          '   📶 Internet\n'
          '   🏛️ Administration\n'
          '   📺 TV / TOD by BeIN\n'
          '   🛡️ Insurance\n'
          '   💼 Finance\n'
          '   🎓 Education\n'
          '   ✈️ Air Transport\n'
          '3️⃣ Choose the company\n'
          '4️⃣ Enter your customer ID\n'
          '5️⃣ Your bill details will appear\n'
          '6️⃣ Enter your secret PIN to pay\n\n'
          '✅ Payment confirmed instantly!',
      'a_ar': '🧾 لتسديد الفواتير:\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على "تسديد الفواتير"\n'
          '2️⃣ اختر نوع الفاتورة:\n'
          '   ⚡ كهرباء\n'
          '   💧 ماء\n'
          '   📶 إنترنت\n'
          '   🏛️ إدارة\n'
          '   📺 تلفزيون / TOD by BeIN\n'
          '   🛡️ تأمين\n'
          '   💼 مالية\n'
          '   🎓 تعليم\n'
          '   ✈️ نقل جوي\n'
          '3️⃣ اختر الشركة\n'
          '4️⃣ أدخل معرّفك (ID)\n'
          '5️⃣ ستظهر تفاصيل فاتورتك\n'
          '6️⃣ أدخل رقمك السري للدفع\n\n'
          '✅ يتم تأكيد الدفع فوراً!',
      'a_fr': '🧾 Pour payer vos factures:\n\n'
          '1️⃣ Sur l\'accueil appuyez "Paiement de factures"\n'
          '2️⃣ Choisissez la catégorie:\n'
          '   ⚡ Électricité\n'
          '   💧 Eau\n'
          '   📶 Internet\n'
          '   🏛️ Administration\n'
          '   📺 TV / TOD by BeIN\n'
          '   🛡️ Assurance\n'
          '   💼 Finance\n'
          '   🎓 Éducation\n'
          '   ✈️ Transport aérien\n'
          '3️⃣ Choisissez la société\n'
          '4️⃣ Entrez votre identifiant client (ID)\n'
          '5️⃣ Les détails de votre facture s\'affichent\n'
          '6️⃣ Entrez votre code PIN pour payer\n\n'
          '✅ Paiement confirmé instantanément!',
    },

    // ── 6. سحب الأموال ───────────────────────────────────────────────────────
    {
      'kw_en': ['withdraw', 'cash out', 'cash withdrawal', 'agency', 'agent', 'withdraw money', 'code'],
      'kw_ar': ['سحب', 'سحب أموال', 'نقود', 'وكالة', 'وكيل', 'كاش', 'استلام مال', 'كود سحب'],
      'kw_fr': ['retrait', 'retirer', 'cash out', 'agence', 'agent', 'code retrait'],
      'a_en': '💵 To withdraw cash:\n\n'
          '1️⃣ Visit the nearest agency\n'
          '2️⃣ In the app tap "Cash out"\n'
          '3️⃣ Enter the agency number or ID\n'
          '4️⃣ Enter the amount to withdraw\n'
          '5️⃣ Enter your secret PIN to confirm\n'
          '6️⃣ You will receive a withdrawal code by SMS\n'
          '7️⃣ Give the code to the agency owner\n'
          '8️⃣ Receive your cash! 💵\n\n'
          '⚠️ Do not share the code with anyone except the agency.',
      'a_ar': '💵 لسحب الأموال نقداً:\n\n'
          '1️⃣ توجه إلى أقرب وكالة منك\n'
          '2️⃣ في التطبيق اضغط على "Cash out"\n'
          '3️⃣ أدخل رقم الوكالة أو معرّفها\n'
          '4️⃣ أدخل المبلغ المراد سحبه\n'
          '5️⃣ أدخل رقمك السري للتأكيد\n'
          '6️⃣ ستصلك رسالة SMS بكود السحب\n'
          '7️⃣ أعطِ الكود لصاحب الوكالة\n'
          '8️⃣ استلم أموالك نقداً! 💵\n\n'
          '⚠️ لا تشارك الكود مع أي شخص غير صاحب الوكالة.',
      'a_fr': '💵 Pour retirer de l\'argent:\n\n'
          '1️⃣ Rendez-vous à l\'agence la plus proche\n'
          '2️⃣ Dans l\'app appuyez "Cash out"\n'
          '3️⃣ Entrez le numéro ou l\'ID de l\'agence\n'
          '4️⃣ Entrez le montant à retirer\n'
          '5️⃣ Entrez votre code PIN pour confirmer\n'
          '6️⃣ Vous recevrez un code de retrait par SMS\n'
          '7️⃣ Donnez le code au responsable de l\'agence\n'
          '8️⃣ Récupérez votre argent! 💵\n\n'
          '⚠️ Ne partagez le code qu\'avec l\'agent.',
    },

    // ── 7. الدفع عند التجار B-Pay ─────────────────────────────────────────────
    {
      'kw_en': ['bpay', 'b-pay', 'merchant', 'merchant payment', 'shop', 'store payment', 'pay merchant', 'merchant id'],
      'kw_ar': ['bpay', 'b-pay', 'تاجر', 'دفع للتاجر', 'متجر', 'محل', 'معرف التاجر', 'شراء', 'دفع عند'],
      'kw_fr': ['bpay', 'b-pay', 'marchand', 'paiement marchand', 'boutique', 'commerçant'],
      'a_en': '🏪 To pay a merchant (B-Pay):\n\n'
          '1️⃣ On the Home screen tap "B-Pay"\n'
          '2️⃣ Enter the merchant ID\n'
          '3️⃣ Enter the amount to pay\n'
          '4️⃣ Enter your secret PIN to confirm\n\n'
          '✅ Payment sent to the merchant instantly!',
      'a_ar': '🏪 للدفع عند التجار (B-Pay):\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على "B-Pay"\n'
          '2️⃣ أدخل معرّف التاجر\n'
          '3️⃣ أدخل المبلغ المراد دفعه\n'
          '4️⃣ أدخل رقمك السري للتأكيد\n\n'
          '✅ يتم إرسال الدفع للتاجر فوراً!',
      'a_fr': '🏪 Pour payer un marchand (B-Pay):\n\n'
          '1️⃣ Sur l\'accueil appuyez "B-Pay"\n'
          '2️⃣ Entrez l\'identifiant du marchand\n'
          '3️⃣ Entrez le montant à payer\n'
          '4️⃣ Entrez votre code PIN pour confirmer\n\n'
          '✅ Paiement envoyé au marchand instantanément!',
    },

    // ── 8. طلب دفتر الشيكات ──────────────────────────────────────────────────
    {
      'kw_en': ['cheque book', 'checkbook', 'cheque', 'check book', 'request cheque'],
      'kw_ar': ['دفتر شيكات', 'شيكات', 'دفتر صكوك', 'طلب شيك', 'شيك'],
      'kw_fr': ['chéquier', 'carnet de chèques', 'chèque', 'demande chéquier'],
      'a_en': '📒 To request a cheque book:\n\n'
          '1️⃣ On the Home screen tap "Accounts"\n'
          '2️⃣ Select "Request Cheque Book"\n'
          '3️⃣ Choose your account\n'
          '4️⃣ Confirm your request\n\n'
          '✅ Your cheque book will be ready within 3–5 business days.',
      'a_ar': '📒 لطلب دفتر شيكات:\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على "الحسابات"\n'
          '2️⃣ اختر "طلب دفتر شيكات"\n'
          '3️⃣ اختر حسابك\n'
          '4️⃣ أكّد الطلب\n\n'
          '✅ سيكون دفتر الشيكات جاهزاً خلال 3-5 أيام عمل.',
      'a_fr': '📒 Pour demander un chéquier:\n\n'
          '1️⃣ Sur l\'accueil appuyez "Comptes"\n'
          '2️⃣ Sélectionnez "Demande de chéquier"\n'
          '3️⃣ Choisissez votre compte\n'
          '4️⃣ Confirmez votre demande\n\n'
          '✅ Votre chéquier sera prêt dans 3 à 5 jours ouvrables.',
    },

    // ── 9. بطاقة الخصم ───────────────────────────────────────────────────────
    {
      'kw_en': ['debit card', 'card', 'bank card', 'request card', 'new card'],
      'kw_ar': ['بطاقة', 'بطاقة خصم', 'بطاقة بنكية', 'طلب بطاقة', 'بطاقة جديدة'],
      'kw_fr': ['carte', 'carte débit', 'carte bancaire', 'demande carte', 'nouvelle carte'],
      'a_en': '💳 Debit Card services:\n\n'
          '1️⃣ On the Home screen tap "Debit Card"\n'
          '2️⃣ You can:\n'
          '   • Request a new card\n'
          '   • View card details\n'
          '   • Freeze / unfreeze your card\n'
          '   • Set spending limits\n\n'
          '✅ Virtual card is available immediately.\n'
          'Physical card delivery: 5–7 business days.',
      'a_ar': '💳 خدمات بطاقة الخصم:\n\n'
          '1️⃣ في الصفحة الرئيسية اضغط على "بطاقة الخصم"\n'
          '2️⃣ يمكنك:\n'
          '   • طلب بطاقة جديدة\n'
          '   • عرض تفاصيل البطاقة\n'
          '   • تجميد / إلغاء تجميد البطاقة\n'
          '   • تحديد حدود الإنفاق\n\n'
          '✅ البطاقة الافتراضية متاحة فوراً.\n'
          'توصيل البطاقة المادية: 5-7 أيام عمل.',
      'a_fr': '💳 Services carte de débit:\n\n'
          '1️⃣ Sur l\'accueil appuyez "Carte débit"\n'
          '2️⃣ Vous pouvez:\n'
          '   • Demander une nouvelle carte\n'
          '   • Voir les détails de la carte\n'
          '   • Geler / dégeler la carte\n'
          '   • Définir les limites de dépenses\n\n'
          '✅ Carte virtuelle disponible immédiatement.\n'
          'Livraison carte physique: 5–7 jours ouvrables.',
    },

    // ── 10. الرقم السري PIN ──────────────────────────────────────────────────
    {
      'kw_en': ['pin', 'secret code', 'password', 'forgot pin', 'change pin', 'reset pin'],
      'kw_ar': ['رقم سري', 'pin', 'كلمة مرور', 'نسيت الرقم', 'تغيير الرقم', 'إعادة تعيين'],
      'kw_fr': ['code pin', 'mot de passe', 'code secret', 'oublié pin', 'changer pin'],
      'a_en': '🔑 About your secret PIN:\n\n'
          '• Your PIN is required for all transactions\n'
          '• Never share your PIN with anyone\n\n'
          'To change your PIN:\n'
          '1️⃣ Go to Settings → Security\n'
          '2️⃣ Tap "Change PIN"\n'
          '3️⃣ Enter current PIN then new PIN\n\n'
          'Forgot your PIN?\n'
          '1️⃣ On login screen tap "Forgot password"\n'
          '2️⃣ Enter your phone number\n'
          '3️⃣ Enter the code received by SMS\n'
          '4️⃣ Set a new PIN\n\n'
          '⚠️ We will NEVER ask for your PIN by phone or message.',
      'a_ar': '🔑 عن رقمك السري:\n\n'
          '• الرقم السري مطلوب لجميع العمليات\n'
          '• لا تشارك رقمك السري مع أي شخص أبداً\n\n'
          'لتغيير الرقم السري:\n'
          '1️⃣ اذهب إلى الإعدادات ← الأمان\n'
          '2️⃣ اضغط "تغيير الرقم السري"\n'
          '3️⃣ أدخل الرقم الحالي ثم الرقم الجديد\n\n'
          'نسيت رقمك السري؟\n'
          '1️⃣ في شاشة تسجيل الدخول اضغط "نسيت كلمة المرور"\n'
          '2️⃣ أدخل رقم هاتفك\n'
          '3️⃣ أدخل الكود الذي وصلك بالـ SMS\n'
          '4️⃣ حدد رقماً سرياً جديداً\n\n'
          '⚠️ لن نطلب منك رقمك السري أبداً عبر الهاتف أو الرسائل.',
      'a_fr': '🔑 À propos de votre code PIN:\n\n'
          '• Le PIN est requis pour toutes les opérations\n'
          '• Ne partagez jamais votre PIN\n\n'
          'Pour changer votre PIN:\n'
          '1️⃣ Allez dans Paramètres → Sécurité\n'
          '2️⃣ Appuyez "Changer le PIN"\n'
          '3️⃣ Entrez l\'ancien puis le nouveau PIN\n\n'
          'PIN oublié?\n'
          '1️⃣ Sur l\'écran de connexion appuyez "Mot de passe oublié"\n'
          '2️⃣ Entrez votre numéro de téléphone\n'
          '3️⃣ Entrez le code reçu par SMS\n'
          '4️⃣ Définissez un nouveau PIN\n\n'
          '⚠️ Nous ne vous demanderons JAMAIS votre PIN.',
    },

  ]; // ── fin _items ────────────────────────────────────────────────────────────

  // ── Language detection ────────────────────────────────────────────────────
  static String detectLang(String t) {
    if (RegExp(r'[\u0600-\u06FF]').hasMatch(t)) return 'ar';
    final fr = ['bonjour','solde','comment','virement','carte','frais','compte',
      'recharge','facture','retrait','payer','agence','chèque','code pin',
      'je','mon','ma','les','des'];
    if (fr.any((w) => t.toLowerCase().contains(w))) return 'fr';
    return 'en';
  }

  // ── Resolve message → answer ──────────────────────────────────────────────
  static Map<String, String> resolve(String msg) {
    final lang = detectLang(msg);
    final lower = msg.toLowerCase();

    if (lower.contains('how are you') ||
        lower.contains('how are u') ||
        lower.contains('how r u') ||
        lower.contains('how is it going')) {
      return {'lang': lang, 'answer': _greeting(lang)};
    }

    // Greetings
    final greet = ['hi','hello','hey','مرحبا','السلام','هلا','أهلا','bonjour','salut','bonsoir','صباح','مساء'];
    if (greet.any((g) => lower.contains(g))) {
      return {'lang': lang, 'answer': _greeting(lang)};
    }

    // Match FAQ
    int best = 0; Map? bestItem;
    for (final item in _items) {
      final kw = (item['kw_$lang'] as List? ?? item['kw_en'] as List)
          .map((k) => k.toString().toLowerCase()).toList();
      int score = 0;
      for (final k in kw) {
        if (lower.contains(k)) score += k.split(' ').length + 1;
      }
      if (score > best) { best = score; bestItem = item; }
    }

    if (bestItem != null && best >= 2) {
      return {'lang': lang, 'answer': bestItem['a_$lang'] ?? bestItem['a_en']};
    }
    return {'lang': lang, 'answer': _fallback(lang)};
  }

  static String _greeting(String l) => {
    'en': '👋 Hello! I\'m your smart financial assistant.\n\nI can help you with:\n\n'
        '• 💰 Check account balance\n'
        '• 📱 Phone recharge (Mauritel / Chinguitel / Mattel)\n'
        '• 💸 Money transfers\n'
        '• 🔄 GIMTEL transfers to other apps\n'
        '• 🧾 Bill payments (Electricity, Water, Internet...)\n'
        '• 💵 Cash withdrawal via agency\n'
        '• 🏪 Merchant payment (B-Pay)\n'
        '• 📒 Request cheque book\n'
        '• 💳 Debit card services\n'
        '• 🔑 PIN management\n\n'
        'What would you like to know?',
    'ar': '👋 مرحباً! أنا مساعدك المالي الذكي.\n\nيمكنني مساعدتك في:\n\n'
        '• 💰 معرفة رصيد الحساب\n'
        '• 📱 شحن الهاتف (موريتل / شنقيتل / ماتل)\n'
        '• 💸 تحويل الأموال\n'
        '• 🔄 تحويل GIMTEL لتطبيقات أخرى\n'
        '• 🧾 دفع الفواتير (كهرباء، ماء، إنترنت...)\n'
        '• 💵 سحب الأموال عبر الوكالة\n'
        '• 🏪 الدفع عند التجار (B-Pay)\n'
        '• 📒 طلب دفتر شيكات\n'
        '• 💳 خدمات بطاقة الخصم\n'
        '• 🔑 إدارة الرقم السري\n\n'
        'بماذا يمكنني مساعدتك؟',
    'fr': '👋 Bonjour! Je suis votre assistant financier intelligent.\n\nJe peux vous aider avec:\n\n'
        '• 💰 Consulter le solde du compte\n'
        '• 📱 Recharge téléphone (Mauritel / Chinguitel / Mattel)\n'
        '• 💸 Transferts d\'argent\n'
        '• 🔄 Transferts GIMTEL vers autres apps\n'
        '• 🧾 Paiement de factures (Électricité, Eau, Internet...)\n'
        '• 💵 Retrait d\'espèces via agence\n'
        '• 🏪 Paiement marchand (B-Pay)\n'
        '• 📒 Demande de chéquier\n'
        '• 💳 Services carte de débit\n'
        '• 🔑 Gestion du code PIN\n\n'
        'Comment puis-je vous aider?',
  }[l]!;

  static String _fallback(String l) => {
    'en': '🤔 I\'m not sure about that.\n\n'
        'I can help with:\n'
        '💰 Balance • 📱 Recharge • 💸 Transfer\n'
        '🔄 GIMTEL • 🧾 Bills • 💵 Cash out\n'
        '🏪 B-Pay • 📒 Cheque • 💳 Card • 🔑 PIN\n\n'
        'Try rephrasing your question!',
    'ar': '🤔 لست متأكداً من فهم سؤالك.\n\n'
        'يمكنني المساعدة في:\n'
        '💰 الرصيد • 📱 الشحن • 💸 التحويل\n'
        '🔄 جيمتل • 🧾 الفواتير • 💵 السحب\n'
        '🏪 B-Pay • 📒 الشيكات • 💳 البطاقة • 🔑 الرقم السري\n\n'
        'حاول إعادة صياغة سؤالك!',
    'fr': '🤔 Je ne suis pas sûr de comprendre.\n\n'
        'Je peux aider avec:\n'
        '💰 Solde • 📱 Recharge • 💸 Transfert\n'
        '🔄 GIMTEL • 🧾 Factures • 💵 Retrait\n'
        '🏪 B-Pay • 📒 Chèques • 💳 Carte • 🔑 PIN\n\n'
        'Essayez de reformuler votre question!',
  }[l]!;
}

// ── App ───────────────────────────────────────────────────────────────────────
class FinAssistApp extends StatefulWidget {
  const FinAssistApp({super.key});
  @override State<FinAssistApp> createState() => _FinAssistAppState();
}

class _FinAssistAppState extends State<FinAssistApp> {
  String _lang = 'ar'; // Default Arabic
  String _screen = 'login';

  void _setLang(String l) => setState(() => _lang = l);
  void _nav(String s) => setState(() => _screen = s);
  void _login() => _nav('chat');
  void _logout() {
    apiService.logout();
    _nav('login');
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'FinAssist',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(brightness: Brightness.dark, scaffoldBackgroundColor: C.navy),
    home: _buildScreen(),
  );

  Widget _buildScreen() {
    switch (_screen) {
      case 'register':
        return RegisterPage(lang: _lang, onLangChange: _setLang, onSuccess: _login, onLogin: () => _nav('login'));
      case 'chat':
        return ChatPage(lang: _lang, onLangChange: _setLang, onHistory: () => _nav('history'), onNewChat: () {}, onLogout: _logout);
      case 'history':
        return HistoryPage(lang: _lang, onBack: () => _nav('chat'));
      default:
        return LoginPage(lang: _lang, onLangChange: _setLang, onSuccess: _login, onRegister: () => _nav('register'));
    }
  }
}

// ── Background ────────────────────────────────────────────────────────────────
class AppBg extends StatefulWidget {
  final Widget child;
  const AppBg({super.key, required this.child});
  @override State<AppBg> createState() => _AppBgState();
}

class _AppBgState extends State<AppBg> with SingleTickerProviderStateMixin {
  late AnimationController _c;
  @override void initState() { super.initState();
    _c = AnimationController(vsync: this, duration: const Duration(seconds: 3))..repeat(reverse: true); }
  @override void dispose() { _c.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => Stack(children: [
    Container(decoration: const BoxDecoration(gradient: LinearGradient(
      begin: Alignment.topLeft, end: Alignment.bottomRight,
      colors: [Color(0xFF0A0E27), Color(0xFF0D1535), Color(0xFF070B1E)]))),
    CustomPaint(size: MediaQuery.of(context).size, painter: _Grid()),
    AnimatedBuilder(animation: _c, builder: (_, __) => Positioned(top: -80, right: -80,
      child: Container(width: 260, height: 260, decoration: BoxDecoration(shape: BoxShape.circle,
        gradient: RadialGradient(colors: [C.gold.withOpacity(0.07 + _c.value * 0.05), Colors.transparent]))))),
    Positioned(bottom: 80, left: -50, child: Container(width: 170, height: 170,
      decoration: BoxDecoration(shape: BoxShape.circle,
        gradient: RadialGradient(colors: [C.mint.withOpacity(0.06), Colors.transparent])))),
    widget.child,
  ]);
}

class _Grid extends CustomPainter {
  @override void paint(Canvas c, Size s) {
    final p = Paint()..color = C.gold.withOpacity(0.025)..strokeWidth = 1;
    for (double x = 0; x < s.width; x += 38) c.drawLine(Offset(x,0), Offset(x,s.height), p);
    for (double y = 0; y < s.height; y += 38) c.drawLine(Offset(0,y), Offset(s.width,y), p);
  }
  @override bool shouldRepaint(_) => false;
}

// ── Shared widgets ────────────────────────────────────────────────────────────
class GoldBtn extends StatelessWidget {
  final String label; final bool loading; final VoidCallback onTap;
  const GoldBtn({super.key, required this.label, required this.onTap, this.loading = false});
  @override
  Widget build(BuildContext context) => GestureDetector(onTap: loading ? null : onTap,
    child: Container(width: double.infinity, height: 52,
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [C.gold, C.goldL]),
        borderRadius: BorderRadius.circular(15),
        boxShadow: [BoxShadow(color: C.gold.withOpacity(0.4), blurRadius: 18, offset: const Offset(0,6))]),
      child: Center(child: loading
        ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(color: C.navy, strokeWidth: 2.5))
        : Text(label, style: GoogleFonts.dmSans(color: C.navy, fontSize: 15, fontWeight: FontWeight.w700)))));
}

// Simple text field used inside the forgot-password dialog
class _DialogField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final bool obscure;
  final TextInputType keyboardType;
  const _DialogField({required this.ctrl, required this.label,
    this.obscure = false, this.keyboardType = TextInputType.text});
  @override
  Widget build(BuildContext context) => TextField(
    controller: ctrl,
    obscureText: obscure,
    keyboardType: keyboardType,
    style: GoogleFonts.dmSans(color: C.text, fontSize: 13),
    decoration: InputDecoration(
      labelText: label,
      labelStyle: GoogleFonts.dmSans(color: C.muted, fontSize: 12),
      filled: true,
      fillColor: C.navyL,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: C.gold.withOpacity(0.2))),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: C.gold.withOpacity(0.2))),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: C.gold)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
    ),
  );
}

class GoldField extends StatelessWidget {
  final String label, hint; final TextEditingController ctrl;
  final String? icon; final bool obscure, hasToggle; final VoidCallback? onToggle;
  const GoldField({super.key, required this.label, required this.hint, required this.ctrl,
    this.icon, this.obscure = false, this.hasToggle = false, this.onToggle});
  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text(label, style: GoogleFonts.dmSans(color: C.muted, fontSize: 10, letterSpacing: 1)),
    const SizedBox(height: 6),
    Container(decoration: BoxDecoration(color: C.navyL, borderRadius: BorderRadius.circular(13),
      border: Border.all(color: C.gold.withOpacity(0.18))),
      child: Row(children: [
        if (icon != null) Padding(padding: const EdgeInsets.only(left: 12),
          child: Text(icon!, style: const TextStyle(fontSize: 15))),
        Expanded(child: TextField(controller: ctrl, obscureText: obscure,
          style: GoogleFonts.dmSans(color: C.text, fontSize: 14),
          decoration: InputDecoration(hintText: hint,
            hintStyle: GoogleFonts.dmSans(color: C.muted.withOpacity(0.5), fontSize: 14),
            border: InputBorder.none,
            contentPadding: EdgeInsets.symmetric(horizontal: icon != null ? 8 : 14, vertical: 13)))),
        if (hasToggle) IconButton(
          icon: Icon(obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined, color: C.muted, size: 18),
          onPressed: onToggle),
      ])),
  ]);
}

class _LangBtn extends StatelessWidget {
  final String lang; final void Function(String) onChange;
  const _LangBtn({required this.lang, required this.onChange});
  String _flag(String l) => {'en':'🇬🇧','ar':'🇸🇦','fr':'🇫🇷'}[l]!;
  @override
  Widget build(BuildContext context) => PopupMenuButton<String>(onSelected: onChange,
    color: C.surface,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: C.gold.withOpacity(0.2))),
    child: Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: C.surfL, borderRadius: BorderRadius.circular(10),
        border: Border.all(color: C.gold.withOpacity(0.2))),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Text(_flag(lang), style: const TextStyle(fontSize: 16)),
        const SizedBox(width: 3),
        Icon(Icons.expand_more_rounded, color: C.gold, size: 14)])),
    itemBuilder: (_) => [
      _mi('ar','🇸🇦','العربية'), _mi('fr','🇫🇷','Français'), _mi('en','🇬🇧','English'),
    ]);
  PopupMenuItem<String> _mi(String v, String f, String n) => PopupMenuItem(value: v,
    child: Row(children: [Text(f, style: const TextStyle(fontSize: 18)), const SizedBox(width: 10),
      Text(n, style: GoogleFonts.dmSans(color: C.text, fontSize: 14)),
      if (v == lang) ...[const Spacer(), Icon(Icons.check_rounded, color: C.gold, size: 16)]]));
}

class _HdrBtn extends StatelessWidget {
  final IconData icon; final VoidCallback onTap;
  const _HdrBtn({required this.icon, required this.onTap});
  @override
  Widget build(BuildContext context) => GestureDetector(onTap: onTap,
    child: Container(width: 34, height: 34, margin: const EdgeInsets.only(right: 6),
      decoration: BoxDecoration(color: C.surfL, borderRadius: BorderRadius.circular(10),
        border: Border.all(color: C.gold.withOpacity(0.2))),
      child: Icon(icon, color: C.gold, size: 17)));
}

Widget _appHeader(String lang, String title, void Function(String) onLangChange, List<Widget> actions) =>
  ClipRRect(child: BackdropFilter(filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
    child: Container(padding: const EdgeInsets.fromLTRB(16,12,16,12),
      decoration: BoxDecoration(color: C.surface.withOpacity(0.78),
        border: Border(bottom: BorderSide(color: C.gold.withOpacity(0.15), width: 1))),
      child: Row(children: [
        Container(width: 36, height: 36,
          decoration: BoxDecoration(gradient: const LinearGradient(colors: [C.gold, C.goldL]),
            borderRadius: BorderRadius.circular(10),
            boxShadow: [BoxShadow(color: C.gold.withOpacity(0.4), blurRadius: 10, offset: const Offset(0,3))]),
          child: const Icon(Icons.auto_awesome, color: C.navy, size: 17)),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: GoogleFonts.playfairDisplay(color: C.gold, fontSize: 16, fontWeight: FontWeight.w700)),
          Row(children: [
            Container(width: 5, height: 5, decoration: const BoxDecoration(color: C.mint, shape: BoxShape.circle)),
            const SizedBox(width: 4),
            Text(T.get(lang, 'tagline'), style: GoogleFonts.dmSans(color: C.muted, fontSize: 10)),
          ]),
        ])),
        ...actions,
        const SizedBox(width: 6),
        _LangBtn(lang: lang, onChange: onLangChange),
      ]))));

// ══════════════════════════════════════════════════════════════════════════════
// LOGIN PAGE
// ══════════════════════════════════════════════════════════════════════════════
class LoginPage extends StatefulWidget {
  final String lang; final void Function(String) onLangChange;
  final VoidCallback onSuccess, onRegister;
  const LoginPage({super.key, required this.lang, required this.onLangChange, required this.onSuccess, required this.onRegister});
  @override State<LoginPage> createState() => _LoginState();
}

class _LoginState extends State<LoginPage> {
  final _u = TextEditingController(); final _p = TextEditingController();
  bool _loading = false, _obscure = true; String? _error;
  bool get _isAr => widget.lang == 'ar';
  String t(String k) => T.get(widget.lang, k);

  void _submit() async {
    if (_u.text.isEmpty || _p.text.isEmpty) return;
    setState(() { _loading = true; _error = null; });
    final ok = await apiService.login(_u.text.trim(), _p.text);
    if (!mounted) return;
    if (ok) {
      widget.onSuccess();
    } else {
      setState(() {
        _loading = false;
        _error = _isAr ? 'اسم المستخدم أو كلمة المرور غير صحيحة' : widget.lang == 'fr' ? 'Identifiants incorrects' : 'Invalid credentials';
      });
    }
  }

  void _showForgotPassword(BuildContext context) {
    final lang = widget.lang;
    final isAr = lang == 'ar';
    final eCtrl = TextEditingController();
    final p1Ctrl = TextEditingController();
    final p2Ctrl = TextEditingController();
    String? dialogError;
    bool loading = false;
    // Step 1 = enter email to find account, Step 2 = set new password
    int step = 1;
    String foundUsername = '';

    showDialog(
      context: context,
      barrierDismissible: !loading,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setS) {

          // ── Step 1: verify account by email ───────────────────────────────
          final step1Content = Column(mainAxisSize: MainAxisSize.min, children: [
            Text(
              isAr ? 'أدخل بريدك الإلكتروني المرتبط بحسابك وسنتحقق من وجوده.'
                  : lang == 'fr' ? 'Entrez l\'adresse e-mail liée à votre compte.'
                  : 'Enter the email address linked to your account.',
              style: GoogleFonts.dmSans(color: C.muted, fontSize: 12),
            ),
            const SizedBox(height: 16),
            _DialogField(
              ctrl: eCtrl,
              label: isAr ? 'البريد الإلكتروني' : lang == 'fr' ? 'Adresse e-mail' : 'Email address',
              keyboardType: TextInputType.emailAddress,
            ),
            if (dialogError != null) ...[
              const SizedBox(height: 10),
              Text(dialogError!, style: GoogleFonts.dmSans(color: C.error, fontSize: 12)),
            ],
          ]);

          // ── Step 2: set new password ───────────────────────────────────────
          final step2Content = Column(mainAxisSize: MainAxisSize.min, children: [
            Container(padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.green.withOpacity(0.3))),
              child: Row(children: [
                const Icon(Icons.check_circle_outline, color: Colors.green, size: 16),
                const SizedBox(width: 8),
                Expanded(child: Text(
                  isAr ? 'تم التحقق من حسابك ✅ أدخل كلمة المرور الجديدة.'
                      : lang == 'fr' ? 'Compte vérifié ✅ Entrez votre nouveau mot de passe.'
                      : 'Account verified ✅ Enter your new password.',
                  style: GoogleFonts.dmSans(color: Colors.green, fontSize: 12),
                )),
              ]),
            ),
            const SizedBox(height: 16),
            _DialogField(
              ctrl: p1Ctrl,
              label: isAr ? 'كلمة المرور الجديدة' : lang == 'fr' ? 'Nouveau mot de passe' : 'New password',
              obscure: true,
            ),
            const SizedBox(height: 10),
            _DialogField(
              ctrl: p2Ctrl,
              label: isAr ? 'تأكيد كلمة المرور' : lang == 'fr' ? 'Confirmer le mot de passe' : 'Confirm new password',
              obscure: true,
            ),
            if (dialogError != null) ...[
              const SizedBox(height: 10),
              Text(dialogError!, style: GoogleFonts.dmSans(color: C.error, fontSize: 12)),
            ],
          ]);

          return Directionality(
            textDirection: isAr ? TextDirection.rtl : TextDirection.ltr,
            child: AlertDialog(
              backgroundColor: C.surface,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(
                  isAr ? '🔑 إعادة تعيين كلمة المرور'
                      : lang == 'fr' ? '🔑 Réinitialiser le mot de passe'
                      : '🔑 Reset Password',
                  style: GoogleFonts.dmSans(color: C.gold, fontWeight: FontWeight.w700, fontSize: 16),
                ),
                const SizedBox(height: 4),
                Text(
                  isAr ? 'الخطوة $step من 2'
                      : lang == 'fr' ? 'Étape $step sur 2'
                      : 'Step $step of 2',
                  style: GoogleFonts.dmSans(color: C.muted, fontSize: 11),
                ),
              ]),
              content: SingleChildScrollView(child: step == 1 ? step1Content : step2Content),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: Text(
                    isAr ? 'إلغاء' : lang == 'fr' ? 'Annuler' : 'Cancel',
                    style: GoogleFonts.dmSans(color: C.muted),
                  ),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: C.gold, foregroundColor: C.navy,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
                  onPressed: loading ? null : () async {
                    setS(() { dialogError = null; loading = true; });

                    // ── Step 1: look up account by email ──────────────────
                    if (step == 1) {
                      if (eCtrl.text.trim().isEmpty) {
                        setS(() { loading = false; dialogError = isAr ? 'يرجى إدخال بريدك الإلكتروني'
                            : lang == 'fr' ? 'Veuillez saisir votre e-mail' : 'Please enter your email'; });
                        return;
                      }
                      final result = await apiService.findAccountByEmail(eCtrl.text.trim());
                      if (!ctx.mounted) return;
                      if (result['found'] == true) {
                        foundUsername = result['username'] ?? '';
                        setS(() { step = 2; loading = false; });
                      } else {
                        setS(() { loading = false; dialogError = isAr
                            ? 'لا يوجد حساب مرتبط بهذا البريد الإلكتروني'
                            : lang == 'fr' ? 'Aucun compte associé à cet e-mail'
                            : 'No account found with this email address'; });
                      }
                      return;
                    }

                    // ── Step 2: reset password ─────────────────────────────
                    if (p1Ctrl.text.length < 8) {
                      setS(() { loading = false; dialogError = isAr ? 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'
                          : lang == 'fr' ? 'Le mot de passe doit contenir au moins 8 caractères'
                          : 'Password must be at least 8 characters'; });
                      return;
                    }
                    if (p1Ctrl.text != p2Ctrl.text) {
                      setS(() { loading = false; dialogError = isAr ? 'كلمتا المرور غير متطابقتين'
                          : lang == 'fr' ? 'Les mots de passe ne correspondent pas'
                          : 'Passwords do not match'; });
                      return;
                    }
                    final result = await apiService.resetPassword(foundUsername, eCtrl.text.trim(), p1Ctrl.text);
                    if (!ctx.mounted) return;
                    if (result['success'] == true) {
                      Navigator.pop(ctx);
                      // Auto-fill username on login screen
                      _u.text = foundUsername;
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text(
                          isAr ? '✅ تم إعادة تعيين كلمة المرور. يمكنك الآن تسجيل الدخول.'
                              : lang == 'fr' ? '✅ Mot de passe réinitialisé. Connectez-vous maintenant.'
                              : '✅ Password reset! You can now log in.',
                          style: GoogleFonts.dmSans(color: Colors.white),
                        ),
                        backgroundColor: Colors.green.shade700,
                        duration: const Duration(seconds: 4),
                      ));
                    } else {
                      setS(() { loading = false; dialogError = result['message']?.toString(); });
                    }
                  },
                  child: loading
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: C.navy))
                      : Text(
                          step == 1
                              ? (isAr ? 'التالي ←' : lang == 'fr' ? 'Suivant →' : 'Next →')
                              : (isAr ? 'تأكيد' : lang == 'fr' ? 'Confirmer' : 'Confirm'),
                          style: GoogleFonts.dmSans(fontWeight: FontWeight.w700)),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: _isAr ? TextDirection.rtl : TextDirection.ltr,
    child: Scaffold(backgroundColor: C.navy, body: AppBg(child: SafeArea(
      child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(children: [
        Align(alignment: _isAr ? Alignment.topLeft : Alignment.topRight, child: _LangBtn(lang: widget.lang, onChange: widget.onLangChange)),
        const SizedBox(height: 32),
        Container(width: 72, height: 72,
          decoration: BoxDecoration(gradient: const LinearGradient(colors: [C.gold, C.goldL]),
            borderRadius: BorderRadius.circular(22),
            boxShadow: [BoxShadow(color: C.gold.withOpacity(0.45), blurRadius: 24, offset: const Offset(0,8))]),
          child: const Icon(Icons.auto_awesome, color: C.navy, size: 32)),
        const SizedBox(height: 14),
        Text('FinAssist', style: GoogleFonts.playfairDisplay(color: C.gold, fontSize: 26, fontWeight: FontWeight.w800)),
        const SizedBox(height: 4),
        Text(t('tagline'), style: GoogleFonts.dmSans(color: C.muted, fontSize: 12)),
        const SizedBox(height: 32),
        Container(padding: const EdgeInsets.all(22),
          decoration: BoxDecoration(color: C.surface.withOpacity(0.85), borderRadius: BorderRadius.circular(24),
            border: Border.all(color: C.gold.withOpacity(0.12)),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 30)]),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(t('welcome'), style: GoogleFonts.playfairDisplay(color: C.text, fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 2),
            Text(_isAr ? 'سجل الدخول إلى حسابك' : widget.lang == 'fr' ? 'Connectez-vous à votre compte' : 'Sign in to your account',
              style: GoogleFonts.dmSans(color: C.muted, fontSize: 12)),
            const SizedBox(height: 20),
            GoldField(label: t('username'), hint: _isAr ? 'أدخل اسم المستخدم' : 'Enter your username', icon: '👤', ctrl: _u),
            const SizedBox(height: 13),
            GoldField(label: t('password'), hint: _isAr ? 'أدخل كلمة المرور' : 'Enter your password',
              icon: '🔒', ctrl: _p, obscure: _obscure, hasToggle: true, onToggle: () => setState(() => _obscure = !_obscure)),
            const SizedBox(height: 8),
            Align(alignment: _isAr ? Alignment.centerLeft : Alignment.centerRight,
              child: GestureDetector(
                onTap: () => _showForgotPassword(context),
                child: Text(t('forgot'), style: GoogleFonts.dmSans(
                  color: C.gold, fontSize: 11,
                  decoration: TextDecoration.underline,
                  decorationColor: C.gold,
                )),
              )),
            if (_error != null) ...[
              const SizedBox(height: 10),
              Container(padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: C.error.withOpacity(0.08), borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: C.error.withOpacity(0.3))),
                child: Row(children: [const Icon(Icons.error_outline, color: C.error, size: 15), const SizedBox(width: 8),
                  Expanded(child: Text(_error!, style: GoogleFonts.dmSans(color: C.error, fontSize: 12)))])),
            ],
            const SizedBox(height: 18),
            GoldBtn(label: _loading ? (_isAr ? 'جاري الدخول...' : widget.lang == 'fr' ? 'Connexion...' : 'Signing in...') : t('login'),
              loading: _loading, onTap: _submit),
          ])),
        const SizedBox(height: 20),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text(t('noAccount'), style: GoogleFonts.dmSans(color: C.muted, fontSize: 13)),
          const SizedBox(width: 5),
          GestureDetector(onTap: widget.onRegister,
            child: Text(t('register'), style: GoogleFonts.dmSans(color: C.gold, fontSize: 13, fontWeight: FontWeight.w600))),
        ]),
        const SizedBox(height: 12),
        Text('🔐 مشفر 256-bit', style: GoogleFonts.dmSans(color: C.muted.withOpacity(0.5), fontSize: 10)),
      ]))))));
}

// ══════════════════════════════════════════════════════════════════════════════
// REGISTER PAGE
// ══════════════════════════════════════════════════════════════════════════════
class RegisterPage extends StatefulWidget {
  final String lang; final void Function(String) onLangChange;
  final VoidCallback onSuccess, onLogin;
  const RegisterPage({super.key, required this.lang, required this.onLangChange, required this.onSuccess, required this.onLogin});
  @override State<RegisterPage> createState() => _RegisterState();
}

class _RegisterState extends State<RegisterPage> {
  final _u = TextEditingController(); final _e = TextEditingController();
  final _ph = TextEditingController(); final _p = TextEditingController(); final _cp = TextEditingController();
  bool _loading = false, _obscure = true; String? _error;
  bool get _isAr => widget.lang == 'ar';
  String t(String k) => T.get(widget.lang, k);

  void _submit() async {
    if (_u.text.isEmpty || _e.text.isEmpty || _p.text.isEmpty) return;
    if (!_e.text.contains('@')) { setState(() => _error = widget.lang == 'fr' ? 'Entrez une adresse email valide' : 'Enter a valid email address'); return; }
    if (_p.text.length < 8) { setState(() => _error = widget.lang == 'fr' ? 'Le mot de passe doit contenir au moins 8 caracteres' : 'Password must be at least 8 characters'); return; }
    if (_p.text != _cp.text) { setState(() => _error = _isAr ? 'كلمتا المرور غير متطابقتين' : widget.lang == 'fr' ? 'Mots de passe différents' : 'Passwords do not match'); return; }
    setState(() { _loading = true; _error = null; });
    final registered = await apiService.register(_u.text.trim(), _e.text.trim(), _p.text, phone: _ph.text.trim());
    var loggedIn = false;
    if (registered) {
      loggedIn = await apiService.isLoggedIn;
      if (!loggedIn) {
        loggedIn = await apiService.login(_u.text.trim(), _p.text);
      }
    }
    if (!mounted) return;
    if (loggedIn) {
      widget.onSuccess();
    } else {
      setState(() {
        _loading = false;
        _error = _isAr ? 'تعذر إنشاء الحساب. تحقق من البيانات وحاول مرة أخرى' : widget.lang == 'fr' ? 'Impossible de créer le compte. Vérifiez les informations' : 'Could not create the account. Check the details and try again';
      });
    }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: _isAr ? TextDirection.rtl : TextDirection.ltr,
    child: Scaffold(backgroundColor: C.navy, body: AppBg(child: SafeArea(
      child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(children: [
        Align(alignment: _isAr ? Alignment.topLeft : Alignment.topRight, child: _LangBtn(lang: widget.lang, onChange: widget.onLangChange)),
        const SizedBox(height: 24),
        Container(width: 62, height: 62,
          decoration: BoxDecoration(gradient: const LinearGradient(colors: [C.gold, C.goldL]),
            borderRadius: BorderRadius.circular(19),
            boxShadow: [BoxShadow(color: C.gold.withOpacity(0.4), blurRadius: 20, offset: const Offset(0,6))]),
          child: const Icon(Icons.auto_awesome, color: C.navy, size: 28)),
        const SizedBox(height: 12),
        Text('FinAssist', style: GoogleFonts.playfairDisplay(color: C.gold, fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 22),
        Container(padding: const EdgeInsets.all(22),
          decoration: BoxDecoration(color: C.surface.withOpacity(0.85), borderRadius: BorderRadius.circular(24),
            border: Border.all(color: C.gold.withOpacity(0.12)),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 30)]),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(t('register'), style: GoogleFonts.playfairDisplay(color: C.text, fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 2),
            Text(_isAr ? 'ابدأ في دقائق' : widget.lang == 'fr' ? 'Commencez en quelques minutes' : 'Get started in minutes',
              style: GoogleFonts.dmSans(color: C.muted, fontSize: 12)),
            const SizedBox(height: 18),
            GoldField(label: t('username'), hint: _isAr ? 'اختر اسم مستخدم' : 'Choose a username', icon: '👤', ctrl: _u),
            const SizedBox(height: 12),
            GoldField(label: t('email'), hint: 'your@email.com', icon: '✉️', ctrl: _e),
            const SizedBox(height: 12),
            GoldField(label: t('phone'), hint: '+222 XX XX XX XX', icon: '📱', ctrl: _ph),
            const SizedBox(height: 12),
            GoldField(label: t('password'), hint: _isAr ? 'كلمة مرور قوية' : 'Strong password',
              icon: '🔒', ctrl: _p, obscure: _obscure, hasToggle: true, onToggle: () => setState(() => _obscure = !_obscure)),
            const SizedBox(height: 12),
            GoldField(label: t('confirm'), hint: _isAr ? 'أعد كتابة كلمة المرور' : 'Repeat password',
              icon: '🔒', ctrl: _cp, obscure: _obscure),
            if (_error != null) ...[
              const SizedBox(height: 10),
              Container(padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: C.error.withOpacity(0.08), borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: C.error.withOpacity(0.3))),
                child: Row(children: [const Icon(Icons.error_outline, color: C.error, size: 15), const SizedBox(width: 8),
                  Expanded(child: Text(_error!, style: GoogleFonts.dmSans(color: C.error, fontSize: 12)))])),
            ],
            const SizedBox(height: 18),
            GoldBtn(label: _loading ? (_isAr ? 'جاري الإنشاء...' : 'Creating...') : t('register'), loading: _loading, onTap: _submit),
          ])),
        const SizedBox(height: 18),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text(t('hasAccount'), style: GoogleFonts.dmSans(color: C.muted, fontSize: 13)),
          const SizedBox(width: 5),
          GestureDetector(onTap: widget.onLogin,
            child: Text(t('login'), style: GoogleFonts.dmSans(color: C.gold, fontSize: 13, fontWeight: FontWeight.w600))),
        ]),
      ]))))));
}

// ══════════════════════════════════════════════════════════════════════════════
// CHAT PAGE
// ══════════════════════════════════════════════════════════════════════════════
class _Msg { final String text, lang; final bool isUser; final DateTime time;
  _Msg({required this.text, required this.isUser, required this.time, this.lang = 'ar'}); }

class ChatPage extends StatefulWidget {
  final String lang; final void Function(String) onLangChange;
  final VoidCallback onHistory, onNewChat, onLogout;
  const ChatPage({super.key, required this.lang, required this.onLangChange,
    required this.onHistory, required this.onNewChat, required this.onLogout});
  @override State<ChatPage> createState() => _ChatState();
}

class _ChatState extends State<ChatPage> {
  final _ctrl = TextEditingController(); final _scroll = ScrollController();
  final List<_Msg> _msgs = []; bool _typing = false;
  String? _sessionId;
  bool get _isAr => widget.lang == 'ar';
  String t(String k) => T.get(widget.lang, k);

  // اقتراحات سريعة مخصصة
  final _sugs = {
    'ar': ['💰 ما هو رصيدي؟', '📱 كيف أشحن هاتفي؟', '💸 كيف أحول الأموال؟', '🔄 ما هي خدمة جيمتل؟', '🧾 كيف أدفع الفواتير؟', '💵 كيف أسحب النقود؟', '🏪 كيف أدفع عند التاجر؟', '🔑 نسيت رقمي السري'],
    'en': ['💰 Check my balance', '📱 Phone recharge', '💸 Transfer money', '🔄 GIMTEL service', '🧾 Pay bills', '💵 Cash withdrawal', '🏪 Merchant payment (B-Pay)', '🔑 Forgot my PIN'],
    'fr': ['💰 Mon solde', '📱 Recharger téléphone', '💸 Transférer de l\'argent', '🔄 Service GIMTEL', '🧾 Payer des factures', '💵 Retirer de l\'argent', '🏪 Paiement marchand (B-Pay)', '🔑 Code PIN oublié'],
  };
  void _send(String text) async {
    if (text.trim().isEmpty) return;
    _ctrl.clear();

    final result = FAQ.resolve(text);
    setState(() {
      _msgs.add(_Msg(text: text, isUser: true, time: DateTime.now(), lang: result['lang']!));
      _typing = true;
    });
    _scrollDown();

    String answer = result['answer']!;
    String lang = result['lang']!;

    // Ask the backend so actions and Gemini fallback run server-side.
    final apiResult = await apiService.sendMessage(text, sessionId: _sessionId);
    if (apiResult != null) {
      if (apiResult['error'] != null) {
        final statusCode = apiResult['status_code'];
        answer = statusCode == null
            ? apiResult['error'].toString()
            : 'Chat backend error ($statusCode): ${apiResult['error']}';
      } else {
        _sessionId = apiResult['session_id']?.toString();
        final botMessage = apiResult['bot_message'];
        if (botMessage is Map && botMessage['content'] != null) {
          answer = botMessage['content'].toString();
        }
        lang = apiResult['lang']?.toString() ?? lang;
      }
    } else {
      answer = 'Chat backend is unavailable. Check that Django is running and the API URL is correct.';
    }

    if (!mounted) return;
    setState(() {
      _typing = false;
      _msgs.add(_Msg(text: answer, isUser: false, time: DateTime.now(), lang: lang));
    });
     _scrollDown();
  }
  // void _send(String text) async {
  //   if (text.trim().isEmpty) return;
  //   _ctrl.clear();
  //   final result = FAQ.resolve(text);
  //   setState(() { _msgs.add(_Msg(text: text, isUser: true, time: DateTime.now(), lang: result['lang']!)); _typing = true; });
  //   _scrollDown();
  //   await Future.delayed(const Duration(milliseconds: 900));
  //   if (!mounted) return;
  //   setState(() { _typing = false; _msgs.add(_Msg(text: result['answer']!, isUser: false, time: DateTime.now(), lang: result['lang']!)); });
  //   _scrollDown();
  // }

  void _scrollDown() => WidgetsBinding.instance.addPostFrameCallback((_) {
    if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent + 200,
      duration: const Duration(milliseconds: 400), curve: Curves.easeOutCubic);
  });

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: _isAr ? TextDirection.rtl : TextDirection.ltr,
    child: Scaffold(backgroundColor: C.navy, body: AppBg(child: SafeArea(child: Column(children: [
      _appHeader(widget.lang, t('appName'), widget.onLangChange, [
        _HdrBtn(icon: Icons.history_rounded, onTap: widget.onHistory),
        _HdrBtn(icon: Icons.add_comment_rounded, onTap: () => setState(() {
          _msgs.clear();
          _sessionId = null;
        })),
        _HdrBtn(icon: Icons.logout_rounded, onTap: widget.onLogout),
      ]),
      Expanded(child: _msgs.isEmpty ? _buildEmpty() : _buildMsgs()),
      if (_typing) _buildTyping(),
      _buildInput(),
    ])))));

  Widget _buildEmpty() {
    final sugs = _sugs[widget.lang] ?? _sugs['ar']!;
    return SingleChildScrollView(padding: const EdgeInsets.all(20), child: Column(children: [
      const SizedBox(height: 16),
      Container(width: 78, height: 78,
        decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: C.gold.withOpacity(0.3), width: 1.5),
          gradient: RadialGradient(colors: [C.gold.withOpacity(0.12), C.gold.withOpacity(0.03)])),
        child: const Icon(Icons.auto_awesome, color: C.gold, size: 34)),
      const SizedBox(height: 14),
      Text(t('welcome'), style: GoogleFonts.playfairDisplay(color: C.text, fontSize: 22, fontWeight: FontWeight.w700)),
      const SizedBox(height: 4),
      Text(t('tagline'), style: GoogleFonts.dmSans(color: C.muted, fontSize: 12)),
      const SizedBox(height: 28),
      Row(children: [Expanded(child: Divider(color: C.surfL)),
        Padding(padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text(t('suggestions'), style: GoogleFonts.dmSans(color: C.muted, fontSize: 11, letterSpacing: 0.5))),
        Expanded(child: Divider(color: C.surfL))]),
      const SizedBox(height: 14),
      Wrap(spacing: 8, runSpacing: 8, alignment: WrapAlignment.center,
        children: sugs.map((s) => _Chip(label: s, onTap: () => _send(s), isAr: _isAr)).toList()),
    ]));
  }

  Widget _buildMsgs() => ListView.builder(controller: _scroll,
    padding: const EdgeInsets.fromLTRB(14,14,14,6),
    itemCount: _msgs.length, itemBuilder: (_, i) => _BubbleW(msg: _msgs[i]));

  Widget _buildTyping() => Padding(padding: const EdgeInsets.fromLTRB(14,0,14,6),
    child: Row(children: [_Av(), const SizedBox(width: 8),
      Container(padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(color: C.botBub, borderRadius: BorderRadius.circular(20),
          border: Border.all(color: C.gold.withOpacity(0.1))),
        child: _Dots())]));

  Widget _buildInput() => ClipRRect(child: BackdropFilter(filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
    child: Container(padding: const EdgeInsets.fromLTRB(14,10,14,22),
      decoration: BoxDecoration(color: C.surface.withOpacity(0.88),
        border: Border(top: BorderSide(color: C.gold.withOpacity(0.12)))),
      child: Row(children: [
        if (_isAr) ...[_sendBtn(), const SizedBox(width: 8)],
        Expanded(child: Container(
          decoration: BoxDecoration(color: C.navyL, borderRadius: BorderRadius.circular(14),
            border: Border.all(color: C.gold.withOpacity(0.2))),
          child: TextField(controller: _ctrl, maxLines: null,
            textAlign: _isAr ? TextAlign.right : TextAlign.left,
            style: GoogleFonts.dmSans(color: C.text, fontSize: 14),
            decoration: InputDecoration(hintText: t('hint'),
              hintStyle: GoogleFonts.dmSans(color: C.muted, fontSize: 14),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11)),
            onSubmitted: _send))),
        if (!_isAr) ...[const SizedBox(width: 8), _sendBtn()],
      ]))));

  Widget _sendBtn() => GestureDetector(onTap: () => _send(_ctrl.text),
    child: Container(width: 46, height: 46,
      decoration: BoxDecoration(gradient: const LinearGradient(colors: [C.gold, C.goldL]),
        borderRadius: BorderRadius.circular(13),
        boxShadow: [BoxShadow(color: C.gold.withOpacity(0.4), blurRadius: 12, offset: const Offset(0,4))]),
      child: Icon(_isAr ? Icons.arrow_back_rounded : Icons.arrow_forward_rounded, color: C.navy, size: 20)));
}

// ══════════════════════════════════════════════════════════════════════════════
// HISTORY PAGE
// ══════════════════════════════════════════════════════════════════════════════
class HistoryPage extends StatefulWidget {
  final String lang; final VoidCallback onBack;
  const HistoryPage({super.key, required this.lang, required this.onBack});
  @override State<HistoryPage> createState() => _HistoryState();
}

class _HistoryState extends State<HistoryPage> {
  bool get _isAr => widget.lang == 'ar';
  String t(String k) => T.get(widget.lang, k);

  final _sample = [
    {'title': 'كيف أشحن هاتفي؟', 'count': 3, 'date': 'اليوم 14:32'},
    {'title': 'ما هو رصيدي؟', 'count': 2, 'date': 'اليوم 11:15'},
    {'title': 'خدمة جيمتل GIMTEL', 'count': 4, 'date': 'أمس 18:42'},
    {'title': 'كيف أدفع الفواتير؟', 'count': 6, 'date': 'أمس 09:11'},
    {'title': 'Comment recharger mon téléphone?', 'count': 3, 'date': '27/04/2026'},
    {'title': 'Cash withdrawal via agency', 'count': 5, 'date': '25/04/2026'},
  ];

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: _isAr ? TextDirection.rtl : TextDirection.ltr,
    child: Scaffold(backgroundColor: C.navy, body: AppBg(child: SafeArea(child: Column(children: [
      _appHeader(widget.lang, t('history'), (_) {}, [
        _HdrBtn(icon: Icons.arrow_back_rounded, onTap: widget.onBack),
      ]),
      Expanded(child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _sample.length,
        itemBuilder: (_, i) {
          final s = _sample[i];
          return GestureDetector(onTap: widget.onBack,
            child: Container(margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(color: C.surface, borderRadius: BorderRadius.circular(16),
                border: Border.all(color: C.gold.withOpacity(0.1)),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.15), blurRadius: 10)]),
              child: Row(children: [
                Container(width: 42, height: 42,
                  decoration: BoxDecoration(borderRadius: BorderRadius.circular(12),
                    gradient: RadialGradient(colors: [C.gold.withOpacity(0.15), C.gold.withOpacity(0.04)]),
                    border: Border.all(color: C.gold.withOpacity(0.2))),
                  child: const Icon(Icons.chat_bubble_rounded, color: C.gold, size: 18)),
                const SizedBox(width: 12),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(s['title'] as String, maxLines: 1, overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.dmSans(color: C.text, fontSize: 13, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 3),
                  Text('${s['count']} ${t("messages")} • ${s['date']}',
                    style: GoogleFonts.dmSans(color: C.muted, fontSize: 11)),
                ])),
                Icon(Icons.chevron_right_rounded, color: C.muted, size: 18),
              ])));
        })),
    ])))));
}

// ── Bubble ────────────────────────────────────────────────────────────────────
class _BubbleW extends StatefulWidget {
  final _Msg msg; const _BubbleW({required this.msg});
  @override State<_BubbleW> createState() => _BubbleState();
}
class _BubbleState extends State<_BubbleW> with SingleTickerProviderStateMixin {
  late AnimationController _c; late Animation<double> _sc, _fa;
  @override void initState() { super.initState();
    _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 320));
    _sc = CurvedAnimation(parent: _c, curve: Curves.easeOutBack);
    _fa = CurvedAnimation(parent: _c, curve: Curves.easeOut);
    _c.forward(); }
  @override void dispose() { _c.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) {
    final u = widget.msg.isUser; final ar = widget.msg.lang == 'ar';
    return FadeTransition(opacity: _fa, child: ScaleTransition(scale: _sc,
      alignment: u ? Alignment.centerRight : Alignment.centerLeft,
      child: Padding(padding: const EdgeInsets.only(bottom: 14),
        child: Row(mainAxisAlignment: u ? MainAxisAlignment.end : MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.end, children: [
          if (!u) ...[_Av(), const SizedBox(width: 8)],
          Flexible(child: Column(crossAxisAlignment: u ? CrossAxisAlignment.end : CrossAxisAlignment.start, children: [
            Container(
              constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.74),
              padding: const EdgeInsets.all(13),
              decoration: BoxDecoration(
                gradient: u ? const LinearGradient(colors: [Color(0xFF1E3A7A), Color(0xFF2A4F9A)], begin: Alignment.topLeft, end: Alignment.bottomRight) : null,
                color: u ? null : C.botBub,
                borderRadius: BorderRadius.only(topLeft: const Radius.circular(20), topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(u ? 20 : 4), bottomRight: Radius.circular(u ? 4 : 20)),
                border: Border.all(color: u ? Colors.white.withOpacity(0.08) : C.gold.withOpacity(0.12)),
                boxShadow: [BoxShadow(color: u ? const Color(0xFF1E3A7A).withOpacity(0.4) : Colors.black.withOpacity(0.2), blurRadius: 12, offset: const Offset(0,4))]),
              child: Directionality(textDirection: ar ? TextDirection.rtl : TextDirection.ltr,
                child: Text(widget.msg.text, style: GoogleFonts.dmSans(color: C.text, fontSize: 13, height: 1.65)))),
            const SizedBox(height: 3),
            Text('${widget.msg.time.hour.toString().padLeft(2,"0")}:${widget.msg.time.minute.toString().padLeft(2,"0")}',
              style: GoogleFonts.dmSans(color: C.muted, fontSize: 9)),
          ])),
          if (u) const SizedBox(width: 8),
        ]))));
  }
}

class _Av extends StatelessWidget {
  @override Widget build(BuildContext context) => Container(width: 30, height: 30,
    decoration: BoxDecoration(shape: BoxShape.circle,
      gradient: const LinearGradient(colors: [C.gold, C.goldL]),
      boxShadow: [BoxShadow(color: C.gold.withOpacity(0.4), blurRadius: 8, offset: const Offset(0,2))]),
    child: const Icon(Icons.auto_awesome, color: C.navy, size: 14));
}

class _Dots extends StatefulWidget { @override State<_Dots> createState() => _DotsState(); }
class _DotsState extends State<_Dots> with SingleTickerProviderStateMixin {
  late AnimationController _c;
  @override void initState() { super.initState(); _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat(); }
  @override void dispose() { _c.dispose(); super.dispose(); }
  @override Widget build(BuildContext context) => AnimatedBuilder(animation: _c,
    builder: (_, __) => Row(mainAxisSize: MainAxisSize.min, children: List.generate(3, (i) {
      final t = ((_c.value - i * 0.33) % 1.0).clamp(0.0, 1.0);
      final y = math.sin(t * math.pi) * 4.5;
      return Transform.translate(offset: Offset(0, -y), child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 2.5), width: 7, height: 7,
        decoration: BoxDecoration(shape: BoxShape.circle, color: C.gold.withOpacity(0.4 + t * 0.6))));
    })));
}

class _Chip extends StatelessWidget {
  final String label; final VoidCallback onTap; final bool isAr;
  const _Chip({required this.label, required this.onTap, this.isAr = false});
  @override Widget build(BuildContext context) => GestureDetector(onTap: onTap,
    child: Container(padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 8),
      decoration: BoxDecoration(color: C.surface, borderRadius: BorderRadius.circular(20),
        border: Border.all(color: C.gold.withOpacity(0.22)),
        boxShadow: [BoxShadow(color: C.gold.withOpacity(0.04), blurRadius: 8)]),
      child: Text(label, textDirection: isAr ? TextDirection.rtl : TextDirection.ltr,
        style: GoogleFonts.dmSans(color: C.gold, fontSize: 12, fontWeight: FontWeight.w500))));
}
