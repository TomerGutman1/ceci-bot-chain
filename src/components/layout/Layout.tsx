import { ReactNode } from "react";
import { 
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarInset
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Home, BarChart3, FileText, MessageSquare, User, Menu } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const navigate = useNavigate();

  // Updated sidebar items - removed rankings, renamed decisions to "מבט מאקרו"
  const sidebarItems = [
    { title: "צ'אט עם CECI", icon: MessageSquare, url: "/" },
    { title: "אודות", icon: Menu, url: "https://www.ceci.org.il/%d7%90%d7%95%d7%93%d7%95%d7%aa-%d7%94%d7%9e%d7%a8%d7%9b%d7%96/", external: true },
    { title: "מבט מאקרו", icon: FileText, url: "/decisions" },
  ];

  const handleMenuClick = (item: any) => {
    if (item.external) {
      window.open(item.url, '_blank');
    } else {
      navigate(item.url);
    }
  };

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="min-h-screen flex w-full bg-gray-50">
        {/* סרגל צד ימני */}
        <Sidebar side="right" variant="sidebar" collapsible="offcanvas">
          <SidebarRail />
          <SidebarContent>
            {/* פרופיל משתמש - במקום החיפוש */}
            <div className="px-3 mb-6 mt-4">
              <div className="flex items-center gap-3 p-3 bg-gray-100 rounded-lg">
                <User className="h-8 w-8 text-gray-600" />
                <span className="text-sm font-medium text-gray-800">ישראל ישראלי</span>
              </div>
            </div>

            {/* תפריט - ללא כותרת */}
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {sidebarItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton 
                        isActive={!item.external && location.pathname === item.url} 
                        onClick={() => handleMenuClick(item)}
                        tooltip={item.title}
                        className="rounded-full"
                      >
                        <item.icon />
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>

            {/* כפתור התחברות - aligned exactly with the chat input box */}
            <div className="absolute bottom-0 right-0 left-0 px-4 mb-4">
              <Button 
                className="w-full bg-ceci-blue hover:bg-blue-700 rounded-full" 
                onClick={() => navigate('/dashboard')}
              >
                התחברות / הרשמה
              </Button>
            </div>
          </SidebarContent>
        </Sidebar>

        {/* תוכן עיקרי */}
        <SidebarInset className="p-6 relative">
          {children}
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default Layout;
