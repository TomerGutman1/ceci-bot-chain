import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Auth = () => {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (fullName.trim() && email.trim()) {
      // Store user data in localStorage for simplicity
      localStorage.setItem('user', JSON.stringify({
        fullName: fullName.trim(),
        email: email.trim(),
        isLoggedIn: true
      }));
      
      // Navigate back to home page
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            התחברות למערכת
          </CardTitle>
          <p className="text-gray-600 mt-2">
            הכנס את פרטיך כדי להתחבר
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fullName">שם מלא</Label>
              <Input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="הכנס את שמך המלא"
                required
                className="text-right"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">כתובת מייל</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="הכנס את כתובת המייל שלך"
                required
                className="text-right"
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full bg-ceci-blue hover:bg-blue-700"
            >
              התחבר
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Auth;