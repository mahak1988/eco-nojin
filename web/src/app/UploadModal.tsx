'use client';

import { useState, useRef } from 'react';
import { X, Upload, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadFile, formatFileSize } from '@/lib/supabase/storage';
import { getSupabaseClient } from '@/lib/supabase/client';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const RESOURCE_TYPES = [
  { id: 'book', label: 'کتاب' },
  { id: 'article', label: 'مقاله' },
  { id: 'thesis', label: 'پایان‌نامه' },
  { id: 'video', label: 'ویدیو' },
  { id: 'podcast', label: 'پادکست' },
];

const CATEGORIES = [
  { id: 'environmental_science', label: 'علوم محیط زیست' },
  { id: 'blockchain', label: 'بلاکچین' },
  { id: 'agriculture', label: 'کشاورزی' },
  { id: 'ai', label: 'هوش مصنوعی' },
  { id: 'economics', label: 'اقتصاد' },
  { id: 'energy', label: 'انرژی' },
];

export default function UploadModal({ isOpen, onClose, onSuccess }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [resourceType, setResourceType] = useState('book');
  const [category, setCategory] = useState('environmental_science');
  const [language, setLanguage] = useState('fa');
  const [author, setAuthor] = useState('');
  const [tags, setTags] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Check file size (max 100MB)
      if (selectedFile.size > 100 * 1024 * 1024) {
        setError('حجم فایل نباید بیشتر از 100MB باشد');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file || !title || !author) {
      setError('لطفا تمام فیلدهای ضروری را پر کنید');
      return;
    }

    setUploading(true);
    setError('');
    setUploadProgress(10);

    try {
      // Upload file
      setUploadProgress(30);
      const uploadResult = await uploadFile(file, 'resources', 'uploads');
      
      if (!uploadResult.success || !uploadResult.url) {
        throw new Error(uploadResult.error || 'آپلود فایل ناموفق بود');
      }

      setUploadProgress(70);

      // Save resource metadata to database
      const supabase = getSupabaseClient();
      const { error: dbError } = await supabase
        .from('resources')
        .insert({
          title,
          description,
          resource_type: resourceType,
          category,
          language,
          author,
          tags: tags.split(',').map(t => t.trim()).filter(Boolean),
          file_url: uploadResult.url,
          cover_color: 'from-green-400 to-emerald-600',
        });

      if (dbError) throw dbError;

      setUploadProgress(100);
      setSuccess(true);

      setTimeout(() => {
        onSuccess?.();
        handleClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setTitle('');
    setDescription('');
    setAuthor('');
    setTags('');
    setError('');
    setSuccess(false);
    setUploadProgress(0);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6 rounded-t-2xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Upload className="w-6 h-6" />
            <h2 className="text-2xl font-bold">آپلود منبع جدید</h2>
          </div>
          <button onClick={handleClose} className="p-2 hover:bg-white/20 rounded-lg transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {success ? (
            <div className="text-center py-12">
              <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">آپلود موفق!</h3>
              <p className="text-gray-600">منبع شما با موفقیت آپلود شد و 10 Eco Token دریافت کردید 🎉</p>
            </div>
          ) : (
            <>
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium mb-2">فایل *</label>
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-green-500 transition"
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-3">
                      <FileText className="w-8 h-8 text-green-600" />
                      <div>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600">کلیک کنید یا فایل را اینجا بکشید</p>
                      <p className="text-sm text-gray-400 mt-1">حداکثر 100MB</p>
                    </div>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf,.epub,.doc,.docx,.mp4,.mp3,.zip"
                />
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium mb-2">عنوان *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none"
                  placeholder="عنوان منبع را وارد کنید"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium mb-2">توضیحات</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none resize-none"
                  rows={3}
                  placeholder="توضیح مختصری درباره منبع"
                />
              </div>

              {/* Grid: Type, Category, Language */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-2">نوع</label>
                  <select
                    value={resourceType}
                    onChange={(e) => setResourceType(e.target.value)}
                    className="w-full px-3 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none"
                  >
                    {RESOURCE_TYPES.map(t => (
                      <option key={t.id} value={t.id}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">دسته‌بندی</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none"
                  >
                    {CATEGORIES.map(c => (
                      <option key={c.id} value={c.id}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">زبان</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-3 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none"
                  >
                    <option value="fa">فارسی</option>
                    <option value="en">English</option>
                    <option value="ar">العربية</option>
                  </select>
                </div>
              </div>

              {/* Author */}
              <div>
                <label className="block text-sm font-medium mb-2">نویسنده *</label>
                <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="w-full px-4 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none"
                  placeholder="نام نویسنده"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium mb-2">تگ‌ها (با کاما جدا کنید)</label>
                <input
                  type="text"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="w-full px-4 py-2 border-2 rounded-lg focus:border-green-500 focus:outline-none"
                  placeholder="climate, environment, science"
                />
              </div>

              {/* Error */}
              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-lg">
                  <AlertCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Progress */}
              {uploading && (
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>در حال آپلود...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        {!success && (
          <div className="sticky bottom-0 bg-gray-50 p-6 rounded-b-2xl flex gap-3">
            <button
              onClick={handleClose}
              disabled={uploading}
              className="flex-1 px-4 py-2 border-2 rounded-lg hover:bg-gray-100 transition disabled:opacity-50"
            >
              انصراف
            </button>
            <button
              onClick={handleUpload}
              disabled={uploading || !file || !title || !author}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> در حال آپلود</>
              ) : (
                <><Upload className="w-4 h-4" /> آپلود و دریافت 10 Eco</>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}