
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { label: "בית", path: "/" },
    { label: "אודות", path: "/about" },
    { label: "דירוגים", path: "/rankings" },
    { label: "איך אנחנו עובדים", path: "/methodology" },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="border-b border-gray-200 bg-white py-4 px-4 md:px-6 sticky top-0 z-40">
      <div className="container mx-auto">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img 
              src="/lovable-uploads/b7118ccc-f6d9-49b8-b34d-4a7f9b454adf.png" 
              alt="CECI Logo" 
              className="h-8 w-auto object-contain"
            />
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1 space-x-reverse">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? "text-ceci-blue bg-blue-50"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="hidden md:flex items-center space-x-2 space-x-reverse">
            <Link to="/dashboard">
              <Button variant="outline" className="font-medium rounded-full">
                התחברות
              </Button>
            </Link>
            <Button className="bg-ceci-blue hover:bg-blue-700 font-medium rounded-full">
              התחל עכשיו
            </Button>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden flex items-center"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? (
              <X className="h-6 w-6 text-ceci-gray" />
            ) : (
              <Menu className="h-6 w-6 text-ceci-gray" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden absolute top-[72px] left-0 right-0 bg-white border-b border-gray-200 py-2 px-4 shadow-lg">
          <nav className="flex flex-col space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-3 rounded-full text-sm font-medium ${
                  isActive(item.path)
                    ? "text-ceci-blue bg-blue-50"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="flex flex-col space-y-2 pt-2 border-t border-gray-200">
              <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>
                <Button variant="outline" className="w-full font-medium rounded-full">
                  התחברות
                </Button>
              </Link>
              <Button
                className="w-full bg-ceci-blue hover:bg-blue-700 font-medium rounded-full"
                onClick={() => setIsMenuOpen(false)}
              >
                התחל עכשיו
              </Button>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Navbar;
