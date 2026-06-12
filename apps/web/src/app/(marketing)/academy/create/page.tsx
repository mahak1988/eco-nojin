"use client";

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, Save, Upload, X, BookOpen, Clock, Users, Award
} from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CreateCoursePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    code: '',
    category: '',
    level: 'beginner',
    duration: '',
    description: '',
    objectives: [''],
    prerequisites: [''],
    standards: []
  });

  const categories = [
    { id: 'hydrology', name: 'هیدرولوژی' },
    { id: 'carbon', name: 'کربن و اقلیم' },
    { id: 'soil', name: 'علم خاک' },
    { id: 'remote_sensing', name: 'سنجش از دور' },
    { id: 'sustainable_agriculture', name: 'کشاورزی پایدار' }
  ];

  const standards = ['FAO', 'IPCC', 'SDGs', 'WMO', 'ISO', 'UNCCD'];

  const handleAddObjective = () => {
    setFormData({
      ...formData,
      objectives: [...formData.objectives, '']
    });
  };

  const handleRemoveObjective = (idx: number) => {
    setFormData({
      ...formData,
      objectives: formData.objectives.filter((_, i) => i !== idx)
    });
  };

  const handleObjectiveChange = (idx: number, value: string) => {
    const newObjectives = [...formData.objectives];
    newObjectives[idx] = value;
    setFormData({ ...formData, objectives: newObjectives });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('دوره با موفقیت ایجاد شد!');
    router.push('/academy');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-emerald-400" />
              <h1 className="text-2xl font-bold text-white">ایجاد دوره جدید</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-6">
          {/* Basic Info */}
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <h2 className="text-xl font-bold text-white mb-4">اطلاعات پایه</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="title" className="text-slate-300">عنوان دوره</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="مبانی هیدرولوژی"
                  className="bg-slate-800 border-slate-700 text-white mt-1"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="code" className="text-slate-300">کد دوره</Label>
                <Input
                  id="code"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value})}
                  placeholder="HYD-101"
                  className="bg-slate-800 border-slate-700 text-white mt-1"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="category" className="text-slate-300">دسته‌بندی</Label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-md px-3 py-2 mt-1"
                  required
                >
                  <option value="">انتخاب کنید</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <Label htmlFor="level" className="text-slate-300">سطح</Label>
                <select
                  id="level"
                  value={formData.level}
                  onChange={(e) => setFormData({...formData, level: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-md px-3 py-2 mt-1"
                >
                  <option value="beginner">مقدماتی</option>
                  <option value="intermediate">متوسط</option>
                  <option value="advanced">پیشرفته</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="duration" className="text-slate-300">مدت دوره (ساعت)</Label>
                <Input
                  id="duration"
                  type="number"
                  value={formData.duration}
                  onChange={(e) => setFormData({...formData, duration: e.target.value})}
                  placeholder="40"
                  className="bg-slate-800 border-slate-700 text-white mt-1"
                  required
                />
              </div>
            </div>
          </Card>

          {/* Description */}
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <h2 className="text-xl font-bold text-white mb-4">توضیحات</h2>
            <div>
              <Label htmlFor="description" className="text-slate-300">توضیحات دوره</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="توضیحات کامل دوره..."
                className="bg-slate-800 border-slate-700 text-white mt-1 min-h-[120px]"
                required
              />
            </div>
          </Card>

          {/* Objectives */}
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">اهداف دوره</h2>
              <Button type="button" variant="outline" size="sm" onClick={handleAddObjective}>
                <Plus className="w-4 h-4 ml-1" />
                افزودن هدف
              </Button>
            </div>
            <div className="space-y-2">
              {formData.objectives.map((obj, idx) => (
                <div key={idx} className="flex gap-2">
                  <Input
                    value={obj}
                    onChange={(e) => handleObjectiveChange(idx, e.target.value)}
                    placeholder={`هدف ${idx + 1}`}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                  {formData.objectives.length > 1 && (
                    <Button
                      type="button"
                      variant="destructive"
                      size="icon"
                      onClick={() => handleRemoveObjective(idx)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Standards */}
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <h2 className="text-xl font-bold text-white mb-4">استانداردها</h2>
            <div className="flex flex-wrap gap-2">
              {standards.map((std) => (
                <Button
                  key={std}
                  type="button"
                  variant={formData.standards.includes(std) ? 'default' : 'outline'}
                  onClick={() => {
                    if (formData.standards.includes(std)) {
                      setFormData({
                        ...formData,
                        standards: formData.standards.filter(s => s !== std)
                      });
                    } else {
                      setFormData({
                        ...formData,
                        standards: [...formData.standards, std]
                      });
                    }
                  }}
                  className={formData.standards.includes(std) ? 'bg-emerald-600' : ''}
                >
                  {std}
                </Button>
              ))}
            </div>
          </Card>

          {/* Submit */}
          <div className="flex gap-4">
            <Button type="submit" className="flex-1 bg-emerald-600 hover:bg-emerald-700">
              <Save className="w-4 h-4 ml-2" />
              ذخیره دوره
            </Button>
            <Button type="button" variant="outline" onClick={() => router.push('/academy')}>
              انصراف
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}