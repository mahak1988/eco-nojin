'use client';
import React from 'react';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Mail, Send, CheckCircle } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function ContactPage() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa' || locale === 'ar' || locale === 'ur';
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setForm({ name: '', email: '', subject: '', message: '' });
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <Mail className="w-16 h-16 text-cyan-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict?.pages?.contact?.title || (isPersian ? 'تماس با ما' : 'Contact Us')}</h1>
          <p className="text-gray-600 dark:text-gray-400">{dict?.pages?.contact?.subtitle || (isPersian ? 'مشتاق شنیدن نظرات شما هستیم' : "We'd love to hear from you")}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          {submitted ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">{isPersian ? 'پیام ارسال شد!' : 'Message Sent!'}</h3>
              <p className="text-gray-600 dark:text-gray-400">{isPersian ? 'به زودی پاسخ می‌دهیم' : 'We will respond soon'}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">{dict?.pages?.contact?.name || (isPersian ? 'نام' : 'Name')}</label>
                <input type="text" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} required
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">{dict?.pages?.contact?.email || 'Email'}</label>
                <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">{dict?.pages?.contact?.subject || (isPersian ? 'موضوع' : 'Subject')}</label>
                <input type="text" value={form.subject} onChange={(e) => setForm({...form, subject: e.target.value})} required
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">{dict?.pages?.contact?.message || (isPersian ? 'پیام' : 'Message')}</label>
                <textarea value={form.message} onChange={(e) => setForm({...form, message: e.target.value})} rows={6} required
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none resize-none" />
              </div>
              <button type="submit"
                className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-cyan-700 hover:to-blue-700 transition flex items-center justify-center gap-2">
                <Send className="w-5 h-5" />
                {dict?.pages?.contact?.send || (isPersian ? 'ارسال' : 'Send')}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
