import React, { useState, useEffect } from 'react';
import { FileText, Image, Video, Calendar, User, Eye, Edit, Trash2, Plus, Search, Filter, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@econojin/ui/button';
import { Input } from '@econojin/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@econojin/ui/card';
import { Badge } from '@econojin/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@econojin/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@econojin/ui/select';

// Types for content management
interface ContentItem {
  id: number;
  title: string;
  type: string;
  status: 'draft' | 'pending_approval' | 'approved' | 'published' | 'archived';
  author: string;
  createdAt: string;
  updatedAt: string;
  publishDate?: string;
  version: number;
}

const ContentManagement: React.FC = () => {
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<ContentItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [contentType, setContentType] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  // Mock data initialization
  useEffect(() => {
    const mockContent: ContentItem[] = [
      {
        id: 1,
        title: 'مقاله درباره کشاورزی پایدار',
        type: 'blog_post',
        status: 'published',
        author: 'admin@example.com',
        createdAt: '2023-06-15T10:30:00Z',
        updatedAt: '2023-06-15T15:45:00Z',
        publishDate: '2023-06-15T12:00:00Z',
        version: 3
      },
      {
        id: 2,
        title: 'صفحه تماس',
        type: 'page',
        status: 'published',
        author: 'editor@example.com',
        createdAt: '2023-06-14T09:15:00Z',
        updatedAt: '2023-06-14T11:20:00Z',
        publishDate: '2023-06-14T10:00:00Z',
        version: 1
      },
      {
        id: 3,
        title: 'محصول کود ارگانیک',
        type: 'product',
        status: 'pending_approval',
        author: 'moderator@example.com',
        createdAt: '2023-06-13T14:20:00Z',
        updatedAt: '2023-06-13T14:20:00Z',
        version: 1
      },
      {
        id: 4,
        title: 'مقاله جدید در حال نوشتن',
        type: 'blog_post',
        status: 'draft',
        author: 'writer@example.com',
        createdAt: '2023-06-12T16:30:00Z',
        updatedAt: '2023-06-12T17:45:00Z',
        version: 2
      },
      {
        id: 5,
        title: 'صفحه درباره ما',
        type: 'page',
        status: 'approved',
        author: 'admin@example.com',
        createdAt: '2023-06-11T08:45:00Z',
        updatedAt: '2023-06-11T12:30:00Z',
        version: 1
      }
    ];

    setContentItems(mockContent);
    setFilteredItems(mockContent);
    setLoading(false);
  }, []);

  // Apply filters whenever search term or filters change
  useEffect(() => {
    let result = [...contentItems];

    // Apply search filter
    if (searchTerm) {
      result = result.filter(item => 
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.author.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply content type filter
    if (contentType !== 'all') {
      result = result.filter(item => item.type === contentType);
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      result = result.filter(item => item.status === statusFilter);
    }

    setFilteredItems(result);
  }, [searchTerm, contentType, statusFilter, contentItems]);

  // Status badge component
  const StatusBadge: React.FC<{ status: ContentItem['status'] }> = ({ status }) => {
    const statusConfig = {
      draft: { text: 'پیش‌نویس', color: 'bg-gray-500', icon: FileText },
      pending_approval: { text: 'در انتظار تأیید', color: 'bg-yellow-500', icon: Clock },
      approved: { text: 'تأیید شده', color: 'bg-blue-500', icon: CheckCircle },
      published: { text: 'منتشر شده', color: 'bg-green-500', icon: Eye },
      archived: { text: 'بایگانی شده', color: 'bg-gray-700', icon: FileText }
    };

    const config = statusConfig[status];
    return (
      <Badge className={`${config.color} text-white`}>
        <config.icon className="w-3 h-3 ml-1" />
        {config.text}
      </Badge>
    );
  };

  // Type badge component
  const TypeBadge: React.FC<{ type: string }> = ({ type }) => {
    const typeConfig = {
      page: { text: 'صفحه', color: 'bg-blue-100 text-blue-800' },
      blog_post: { text: 'مقاله', color: 'bg-green-100 text-green-800' },
      product: { text: 'محصول', color: 'bg-purple-100 text-purple-800' },
      media: { text: 'رسانه', color: 'bg-yellow-100 text-yellow-800' }
    };

    const config = typeConfig[type as keyof typeof typeConfig] || { text: type, color: 'bg-gray-100 text-gray-800' };
    return (
      <Badge variant="outline" className={config.color}>
        {config.text}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">مدیریت محتوا</h1>
        <p className="text-muted-foreground">
          مدیریت و نظارت بر تمام محتوای سایت
        </p>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>فیلترها</CardTitle>
          <CardDescription>
            جستجو و فیلتر محتواها بر اساس نوع و وضعیت
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">جستجو</label>
              <div className="relative">
                <Search className="absolute right-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="جستجو در عنوان یا نویسنده..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pr-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">نوع محتوا</label>
              <Select value={contentType} onValueChange={setContentType}>
                <SelectTrigger>
                  <SelectValue placeholder="همه انواع" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه انواع</SelectItem>
                  <SelectItem value="page">صفحه</SelectItem>
                  <SelectItem value="blog_post">مقاله</SelectItem>
                  <SelectItem value="product">محصول</SelectItem>
                  <SelectItem value="media">رسانه</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">وضعیت</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="همه وضعیت‌ها" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه وضعیت‌ها</SelectItem>
                  <SelectItem value="draft">پیش‌نویس</SelectItem>
                  <SelectItem value="pending_approval">در انتظار تأیید</SelectItem>
                  <SelectItem value="approved">تأیید شده</SelectItem>
                  <SelectItem value="published">منتشر شده</SelectItem>
                  <SelectItem value="archived">بایگانی شده</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button className="w-full">
                <Plus className="w-4 h-4 ml-2" />
                محتوای جدید
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Items List */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="all">همه ({contentItems.length})</TabsTrigger>
          <TabsTrigger value="published">منتشر شده ({contentItems.filter(i => i.status === 'published').length})</TabsTrigger>
          <TabsTrigger value="pending">در انتظار ({contentItems.filter(i => i.status === 'pending_approval').length})</TabsTrigger>
          <TabsTrigger value="draft">پیش‌نویس ({contentItems.filter(i => i.status === 'draft').length})</TabsTrigger>
          <TabsTrigger value="approved">تأیید شده ({contentItems.filter(i => i.status === 'approved').length})</TabsTrigger>
          <TabsTrigger value="pages">صفحات ({contentItems.filter(i => i.type === 'page').length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredItems.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-1">محتوایی یافت نشد</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  محتوایی با فیلترهای اعمال شده وجود ندارد
                </p>
                <Button>ایجاد محتوای جدید</Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {filteredItems.map((item) => (
                <Card key={item.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-16 h-16 bg-muted rounded-lg flex items-center justify-center">
                        {item.type === 'blog_post' ? (
                          <FileText className="h-8 w-8 text-muted-foreground" />
                        ) : item.type === 'page' ? (
                          <FileText className="h-8 w-8 text-muted-foreground" />
                        ) : item.type === 'product' ? (
                          <Image className="h-8 w-8 text-muted-foreground" />
                        ) : (
                          <FileText className="h-8 w-8 text-muted-foreground" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-medium truncate">{item.title}</h3>
                            <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <User className="h-4 w-4" />
                                <span>{item.author}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Calendar className="h-4 w-4" />
                                <span>{new Date(item.updatedAt).toLocaleDateString('fa-IR')}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex flex-col items-end gap-2">
                            <div className="flex items-center gap-2">
                              <TypeBadge type={item.type} />
                              <StatusBadge status={item.status} />
                            </div>
                            <div className="text-xs text-muted-foreground">
                              نسخه {item.version}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 mt-3">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 ml-2" />
                            مشاهده
                          </Button>
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4 ml-2" />
                            ویرایش
                          </Button>
                          <Button variant="outline" size="sm" className="text-destructive">
                            <Trash2 className="h-4 w-4 ml-2" />
                            حذف
                          </Button>
                          {item.status === 'pending_approval' && (
                            <Button size="sm" className="bg-green-600 hover:bg-green-700">
                              <CheckCircle className="h-4 w-4 ml-2" />
                              تأیید
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContentManagement;