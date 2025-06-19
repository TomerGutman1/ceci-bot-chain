import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, Users, Globe, Home, Briefcase, TrendingUp, Receipt, Building, 
  Car, Zap, Droplets, TreePine, Wheat, House, MapPin, Heart, 
  UserPlus, User, HelpingHand, GraduationCap, BookOpen, Palette, 
  Activity, Landmark, Plane, Church, Cpu, Lock, Tv, Scale
} from 'lucide-react';

interface PolicyTag {
  name: string;
  icon: React.ReactNode;
  keywords: string[];
  color: string;
}

const POLICY_CATEGORIES: Record<string, PolicyTag[]> = {
  "ביטחון וחוץ": [
    { 
      name: "ביטחון לאומי וצה״ל", 
      icon: <Shield className="w-4 h-4" />, 
      keywords: ["ביטחון", "צבא", "צה״ל", "הגנה"],
      color: "bg-red-100 text-red-700"
    },
    { 
      name: "ביטחון פנים וחירום אזרחי", 
      icon: <Shield className="w-4 h-4" />, 
      keywords: ["משטרה", "חירום", "פיקוד העורף"],
      color: "bg-orange-100 text-orange-700"
    },
    { 
      name: "דיפלומטיה ויחסים בינ״ל", 
      icon: <Globe className="w-4 h-4" />, 
      keywords: ["יחסי חוץ", "שגרירות", "דיפלומטיה"],
      color: "bg-blue-100 text-blue-700"
    },
  ],
  "כלכלה ותעסוקה": [
    { 
      name: "כלכלה מאקרו ותקציב", 
      icon: <TrendingUp className="w-4 h-4" />, 
      keywords: ["תקציב", "כלכלה", "אוצר"],
      color: "bg-green-100 text-green-700"
    },
    { 
      name: "תעסוקה ושוק העבודה", 
      icon: <Briefcase className="w-4 h-4" />, 
      keywords: ["עבודה", "תעסוקה", "שכר"],
      color: "bg-purple-100 text-purple-700"
    },
    { 
      name: "פיננסים, ביטוח ומסים", 
      icon: <Receipt className="w-4 h-4" />, 
      keywords: ["מסים", "ביטוח", "בנקים"],
      color: "bg-yellow-100 text-yellow-700"
    },
  ],
  "תשתיות וסביבה": [
    { 
      name: "תחבורה ציבורית ותשתיות דרך", 
      icon: <Car className="w-4 h-4" />, 
      keywords: ["תחבורה", "כבישים", "רכבת"],
      color: "bg-gray-100 text-gray-700"
    },
    { 
      name: "אנרגיה", 
      icon: <Zap className="w-4 h-4" />, 
      keywords: ["חשמל", "גז", "אנרגיה מתחדשת"],
      color: "bg-amber-100 text-amber-700"
    },
    { 
      name: "מים ותשתיות מים", 
      icon: <Droplets className="w-4 h-4" />, 
      keywords: ["מים", "ביוב", "התפלה"],
      color: "bg-cyan-100 text-cyan-700"
    },
    { 
      name: "סביבה, אקלים ומגוון ביולוגי", 
      icon: <TreePine className="w-4 h-4" />, 
      keywords: ["סביבה", "אקלים", "קיימות"],
      color: "bg-emerald-100 text-emerald-700"
    },
  ],
  "חברה ורווחה": [
    { 
      name: "בריאות ורפואה", 
      icon: <Heart className="w-4 h-4" />, 
      keywords: ["בריאות", "רפואה", "בתי חולים"],
      color: "bg-rose-100 text-rose-700"
    },
    { 
      name: "רווחה ושירותים חברתיים", 
      icon: <UserPlus className="w-4 h-4" />, 
      keywords: ["רווחה", "סעד", "משפחות"],
      color: "bg-pink-100 text-pink-700"
    },
    { 
      name: "אזרחים ותיקים", 
      icon: <User className="w-4 h-4" />, 
      keywords: ["קשישים", "פנסיה", "גמלאים"],
      color: "bg-indigo-100 text-indigo-700"
    },
    { 
      name: "שוויון חברתי וזכויות אדם", 
      icon: <Scale className="w-4 h-4" />, 
      keywords: ["שוויון", "זכויות", "נגישות"],
      color: "bg-purple-100 text-purple-700"
    },
  ],
  "חינוך ותרבות": [
    { 
      name: "חינוך", 
      icon: <GraduationCap className="w-4 h-4" />, 
      keywords: ["חינוך", "בתי ספר", "תלמידים"],
      color: "bg-blue-100 text-blue-700"
    },
    { 
      name: "השכלה גבוהה ומחקר", 
      icon: <BookOpen className="w-4 h-4" />, 
      keywords: ["אוניברסיטאות", "מחקר", "סטודנטים"],
      color: "bg-violet-100 text-violet-700"
    },
    { 
      name: "תרבות ואמנות", 
      icon: <Palette className="w-4 h-4" />, 
      keywords: ["תרבות", "אמנות", "תיאטרון"],
      color: "bg-fuchsia-100 text-fuchsia-700"
    },
    { 
      name: "ספורט ואורח חיים פעיל", 
      icon: <Activity className="w-4 h-4" />, 
      keywords: ["ספורט", "כושר", "אולימפיאדה"],
      color: "bg-lime-100 text-lime-700"
    },
  ],
  "דיגיטל וטכנולוגיה": [
    { 
      name: "טכנולוגיה, חדשנות ודיגיטל", 
      icon: <Cpu className="w-4 h-4" />, 
      keywords: ["טכנולוגיה", "היי-טק", "חדשנות"],
      color: "bg-sky-100 text-sky-700"
    },
    { 
      name: "סייבר ואבטחת מידע", 
      icon: <Lock className="w-4 h-4" />, 
      keywords: ["סייבר", "אבטחה", "פרטיות"],
      color: "bg-red-100 text-red-700"
    },
    { 
      name: "תקשורת ומדיה", 
      icon: <Tv className="w-4 h-4" />, 
      keywords: ["תקשורת", "מדיה", "שידור"],
      color: "bg-purple-100 text-purple-700"
    },
  ]
};

const PolicyTagsGuide: React.FC = () => {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-2xl">🏷️ מדריך תגיות מדיניות</CardTitle>
          <CardDescription>
            רשימת כל התגיות הזמינות במערכת לחיפוש החלטות ממשלה. 
            לחץ על תגית או השתמש במילות המפתח לחיפוש מדויק יותר.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(POLICY_CATEGORIES).map(([category, tags]) => (
          <Card key={category} className="h-fit">
            <CardHeader>
              <CardTitle className="text-lg">{category}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {tags.map((tag) => (
                <div key={tag.name} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className={`p-1.5 rounded ${tag.color}`}>
                      {tag.icon}
                    </span>
                    <span className="font-medium text-sm">{tag.name}</span>
                  </div>
                  <div className="flex flex-wrap gap-1 mr-6">
                    {tag.keywords.map((keyword) => (
                      <Badge 
                        key={keyword} 
                        variant="secondary" 
                        className="text-xs cursor-pointer hover:bg-gray-300"
                        onClick={() => {
                          // This could be connected to the chat interface
                          console.log(`Search for: ${keyword}`);
                        }}
                      >
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">💡 טיפים לחיפוש</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>• השתמש בשם התגית המלא לחיפוש מדויק (למשל: "ביטחון לאומי וצה״ל")</p>
          <p>• אפשר לחפש גם לפי מילות מפתח (למשל: "צבא", "הגנה")</p>
          <p>• לחיפוש מרובה תגיות, שלב ביניהן עם "או" (למשל: "חינוך או בריאות")</p>
          <p>• הוסף מגבלת זמן לחיפוש (למשל: "החלטות משנה האחרונה בנושא חינוך")</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PolicyTagsGuide;
