/**
 * Personal Workspace Component
 * User's personalized dashboard with favorites, presets, and custom views
 */

import React, { useState } from 'react';
import { 
  Star, 
  Heart, 
  Bookmark, 
  Settings, 
  Trash2, 
  Edit, 
  Plus,
  Folder,
  Tag,
  Clock,
  Eye,
  MoreVertical,
  Pin,
  Search
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { formatHebrewDate, formatRelativeTime, getDefaultFilters } from '../../utils/dataTransformers';
import type { DashboardFilters, DashboardDecision, UserPreferences } from '../../types/decision';

interface PersonalWorkspaceProps {
  userPreferences: UserPreferences;
  onPreferencesChange: (preferences: UserPreferences) => void;
  className?: string;
}

interface SavedFilter {
  id: string;
  name: string;
  description: string;
  filters: DashboardFilters;
  isDefault: boolean;
  isPinned: boolean;
  createdAt: Date;
  lastUsed: Date;
  useCount: number;
  tags: string[];
}

interface FavoriteDecision {
  id: string;
  decision: DashboardDecision;
  notes: string;
  tags: string[];
  savedAt: Date;
}

export default function PersonalWorkspace({
  userPreferences,
  onPreferencesChange,
  className,
}: PersonalWorkspaceProps) {
  const [savedFilters, setSavedFilters] = useState<SavedFilter[]>([
    {
      id: '1',
      name: 'החלטות ממשלה נוכחית',
      description: 'החלטות ממשלה 37 מהשנה האחרונה',
      filters: { ...getDefaultFilters(), governments: [37] },
      isDefault: true,
      isPinned: true,
      createdAt: new Date('2024-01-15'),
      lastUsed: new Date(),
      useCount: 25,
      tags: ['ממשלה נוכחית', 'שנה אחרונה'],
    },
    {
      id: '2',
      name: 'החלטות חינוך ובריאות',
      description: 'מיקוד בתחומי החינוך והבריאות',
      filters: { ...getDefaultFilters(), policyAreas: ['חינוך', 'בריאות'] },
      isDefault: false,
      isPinned: false,
      createdAt: new Date('2024-02-10'),
      lastUsed: new Date('2024-12-01'),
      useCount: 12,
      tags: ['חינוך', 'בריאות'],
    },
  ]);

  const [favoriteDecisions, setFavoriteDecisions] = useState<FavoriteDecision[]>([]);
  const [showCreateFilter, setShowCreateFilter] = useState(false);
  const [editingFilter, setEditingFilter] = useState<SavedFilter | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [newFilter, setNewFilter] = useState({
    name: '',
    description: '',
    tags: '',
  });

  // Filter saved filters based on search
  const filteredSavedFilters = savedFilters.filter(filter =>
    filter.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    filter.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    filter.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const togglePin = (filterId: string) => {
    setSavedFilters(prev =>
      prev.map(filter =>
        filter.id === filterId
          ? { ...filter, isPinned: !filter.isPinned }
          : filter
      )
    );
  };

  const deleteFilter = (filterId: string) => {
    setSavedFilters(prev => prev.filter(filter => filter.id !== filterId));
  };

  const createFilter = () => {
    const filter: SavedFilter = {
      id: Date.now().toString(),
      name: newFilter.name,
      description: newFilter.description,
      filters: getDefaultFilters(), // In real app, would use current filters
      isDefault: false,
      isPinned: false,
      createdAt: new Date(),
      lastUsed: new Date(),
      useCount: 0,
      tags: newFilter.tags.split(',').map(tag => tag.trim()).filter(Boolean),
    };

    setSavedFilters(prev => [...prev, filter]);
    setNewFilter({ name: '', description: '', tags: '' });
    setShowCreateFilter(false);
  };

  const addToFavorites = (decision: DashboardDecision, notes: string = '', tags: string[] = []) => {
    const favorite: FavoriteDecision = {
      id: Date.now().toString(),
      decision,
      notes,
      tags,
      savedAt: new Date(),
    };

    setFavoriteDecisions(prev => [...prev, favorite]);
  };

  const removeFromFavorites = (favoriteId: string) => {
    setFavoriteDecisions(prev => prev.filter(fav => fav.id !== favoriteId));
  };

  const getMostUsedFilters = () => {
    return [...savedFilters]
      .sort((a, b) => b.useCount - a.useCount)
      .slice(0, 3);
  };

  const getRecentFilters = () => {
    return [...savedFilters]
      .sort((a, b) => b.lastUsed.getTime() - a.lastUsed.getTime())
      .slice(0, 5);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="h-5 w-5" />
          סביבת עבודה אישית
        </CardTitle>
        <CardDescription>
          מסננים שמורים, החלטות מועדפות והגדרות אישיות
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="filters" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="filters">מסננים שמורים</TabsTrigger>
            <TabsTrigger value="favorites">החלטות מועדפות</TabsTrigger>
            <TabsTrigger value="settings">הגדרות</TabsTrigger>
          </TabsList>

          <TabsContent value="filters" className="space-y-4">
            {/* Search and Create */}
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="חיפוש מסננים..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pr-10 text-right"
                />
              </div>
              
              <Dialog open={showCreateFilter} onOpenChange={setShowCreateFilter}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    חדש
                  </Button>
                </DialogTrigger>
                
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>מסנן חדש</DialogTitle>
                    <DialogDescription>
                      שמור את המסננים הנוכחיים לשימוש חוזר
                    </DialogDescription>
                  </DialogHeader>
                  
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="filter-name">שם המסנן</Label>
                      <Input
                        id="filter-name"
                        value={newFilter.name}
                        onChange={(e) => setNewFilter(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="החלטות ממשלה נוכחית..."
                        className="text-right"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="filter-description">תיאור</Label>
                      <Textarea
                        id="filter-description"
                        value={newFilter.description}
                        onChange={(e) => setNewFilter(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="תיאור קצר של המסנן..."
                        className="text-right"
                        rows={3}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="filter-tags">תגיות (מופרדות בפסיקים)</Label>
                      <Input
                        id="filter-tags"
                        value={newFilter.tags}
                        onChange={(e) => setNewFilter(prev => ({ ...prev, tags: e.target.value }))}
                        placeholder="ממשלה נוכחית, חינוך, בריאות"
                        className="text-right"
                      />
                    </div>
                  </div>
                  
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowCreateFilter(false)}>
                      ביטול
                    </Button>
                    <Button onClick={createFilter} disabled={!newFilter.name}>
                      שמור
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>

            {/* Quick Access - Pinned & Most Used */}
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Pin className="h-4 w-4" />
                  גישה מהירה
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {savedFilters
                    .filter(filter => filter.isPinned)
                    .map((filter) => (
                      <Button
                        key={filter.id}
                        variant="outline"
                        className="h-auto p-3 justify-start"
                      >
                        <div className="text-right">
                          <div className="font-medium">{filter.name}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            {filter.useCount} שימושים
                          </div>
                        </div>
                      </Button>
                    ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Star className="h-4 w-4" />
                  הכי פופולריים
                </h4>
                <div className="space-y-2">
                  {getMostUsedFilters().map((filter) => (
                    <div
                      key={filter.id}
                      className="flex items-center justify-between p-2 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1 text-right">
                        <div className="font-medium">{filter.name}</div>
                        <div className="text-sm text-gray-500">{filter.description}</div>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {filter.useCount}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* All Saved Filters */}
            <div>
              <h4 className="font-medium mb-2">כל המסננים השמורים</h4>
              <div className="space-y-2">
                {filteredSavedFilters.map((filter) => (
                  <div
                    key={filter.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1 text-right">
                      <div className="flex items-center gap-2">
                        <h5 className="font-medium">{filter.name}</h5>
                        {filter.isDefault && <Badge variant="outline" className="text-xs">ברירת מחדל</Badge>}
                        {filter.isPinned && <Pin className="h-3 w-3 text-blue-500" />}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">{filter.description}</p>
                      
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>נוצר {formatRelativeTime(filter.createdAt)}</span>
                        <span>שימוש אחרון {formatRelativeTime(filter.lastUsed)}</span>
                        <span>{filter.useCount} שימושים</span>
                      </div>
                      
                      {filter.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {filter.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              <Tag className="h-2 w-2 mr-1" />
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>
                          <Eye className="h-4 w-4 mr-2" />
                          הפעל
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => togglePin(filter.id)}>
                          <Pin className="h-4 w-4 mr-2" />
                          {filter.isPinned ? 'הסר נעיצה' : 'נעץ'}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setEditingFilter(filter)}>
                          <Edit className="h-4 w-4 mr-2" />
                          ערוך
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => deleteFilter(filter.id)}
                          className="text-red-600"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          מחק
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="favorites" className="space-y-4">
            {favoriteDecisions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Heart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <h3 className="font-medium mb-2">אין החלטות מועדפות</h3>
                <p className="text-sm">
                  החלטות שתסמן כמועדפות יופיעו כאן
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {favoriteDecisions.map((favorite) => (
                  <Card key={favorite.id}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 text-right">
                          <h5 className="font-medium line-clamp-2">
                            {favorite.decision.title}
                          </h5>
                          <div className="text-sm text-gray-500 mt-1">
                            החלטה {favorite.decision.number} • ממשלה {favorite.decision.government}
                          </div>
                          
                          {favorite.notes && (
                            <p className="text-sm text-gray-600 mt-2 p-2 bg-gray-50 rounded">
                              {favorite.notes}
                            </p>
                          )}
                          
                          <div className="flex items-center justify-between mt-3">
                            <div className="text-xs text-gray-400">
                              נשמר {formatRelativeTime(favorite.savedAt)}
                            </div>
                            
                            {favorite.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {favorite.tags.map((tag, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFromFavorites(favorite.id)}
                        >
                          <Heart className="h-4 w-4 fill-current text-red-500" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <div className="space-y-6">
              <div>
                <h4 className="font-medium mb-3">העדפות תצוגה</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="default-view">תצוגת ברירת מחדל</Label>
                    <select
                      id="default-view"
                      value={userPreferences.defaultView}
                      onChange={(e) => onPreferencesChange({
                        ...userPreferences,
                        defaultView: e.target.value as any
                      })}
                      className="border rounded px-2 py-1 text-sm"
                    >
                      <option value="cards">כרטיסים</option>
                      <option value="table">טבלה</option>
                      <option value="list">רשימה</option>
                    </select>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <Label htmlFor="theme">ערכת צבעים</Label>
                    <select
                      id="theme"
                      value={userPreferences.theme}
                      onChange={(e) => onPreferencesChange({
                        ...userPreferences,
                        theme: e.target.value as any
                      })}
                      className="border rounded px-2 py-1 text-sm"
                    >
                      <option value="light">בהיר</option>
                      <option value="dark">כהה</option>
                      <option value="auto">אוטומטי</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-3">סטטיסטיקות שימוש</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="font-medium text-gray-900">
                      {savedFilters.length}
                    </div>
                    <div className="text-gray-500">מסננים שמורים</div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="font-medium text-gray-900">
                      {favoriteDecisions.length}
                    </div>
                    <div className="text-gray-500">החלטות מועדפות</div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}