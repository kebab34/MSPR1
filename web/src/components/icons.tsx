// Ce fichier réexporte les icônes de la librairie lucide-react sous des noms préfixés "Icon"
// Pourquoi ? Pour avoir des noms cohérents dans tout le projet sans importer lucide-react partout

export {
  Timer as IconTimer,             // icône chronomètre → sessions sport
  Plus as IconPlus,               // icône + → bouton d'ajout
  AlertCircle as IconAlertCircle, // icône cercle d'alerte → messages d'erreur
  CheckCircle2 as IconCheck,      // icône coche → messages de succès
  Calendar as IconCalendar,       // icône calendrier → sélecteur de date
  Zap as IconZap,                 // icône éclair → énergie / calories
  Dumbbell as IconDumbbell,       // icône haltère → exercices
  Search as IconSearch,           // icône loupe → barre de recherche
  Shield as IconShield,           // icône bouclier → accès admin
  User as IconUser,               // icône personne → profil utilisateur
  Star as IconStar,               // icône étoile → abonnement premium
  Users as IconUsers,             // icône groupe → liste utilisateurs
  Leaf as IconLeaf,               // icône feuille → aliments / nutrition
  BookOpen as IconBook,           // icône livre ouvert → journal alimentaire
  Activity as IconActivity,       // icône graphe d'activité → mesures / logo
  ChevronRight as IconChevronRight, // icône flèche droite → liens de navigation
  Flame as IconFlame,             // icône flamme → calories brûlées
  Heart as IconHeart,             // icône cœur → fréquence cardiaque
  Moon as IconMoon,               // icône lune → sommeil
  BarChart2 as IconBarChart,      // icône graphe en barres → analytics
  LogOut as IconLogOut,           // icône déconnexion → bouton logout
  Home as IconHome,               // icône maison → page d'accueil
  LineChart as IconLineChart,     // icône graphe en ligne → courbes
  Menu as IconMenu,               // icône hamburger → menu mobile
  X as IconX,                     // icône croix → fermer un panneau
  Trash2 as IconTrash,            // icône poubelle → supprimer
  Download as IconDownload,       // icône téléchargement → export CSV
  Camera as IconCamera,           // icône appareil photo → analyse nutrition IA
  Brain as IconBrain,             // icône cerveau → recommandations IA
  Sparkles as IconSparkles,       // icône sparkles → fonctionnalités IA
  Upload as IconUpload,           // icône upload → envoi de fichier
  ChevronDown as IconChevronDown, // icône flèche bas → accordéon
} from "lucide-react";

export type { LucideProps } from "lucide-react"; // exporte le type des props des icônes (size, className, etc.)
