"use client";

import Link from 'next/link';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import { useState } from 'react';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import {
  Home, Map, GraduationCap, Cloud, Droplets, Activity,
  Coins, BarChart3, Leaf, Menu, X, Sprout, Mountain, Satellite, Brain
} from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const mainLinks = [
    { href: '/', label: 'خانه', icon: Home },
    { href: '/academy', label: 'آکادمی', icon: GraduationCap },
    { href: '/gis', label: 'GIS', icon: Map },
    { href: '/weather', label: 'هواشناسی', icon: Cloud },
    { href: '/drought', label: 'خشکسالی', icon: Mountain },
    { href: '/iot', label: 'IoT', icon: Activity },
    { href: '/ecocoin', label: 'EcoCoin', icon: Coins },
    { href: '/mrv', label: 'MRV', icon: BarChart3 },
    { href: '/soil-water', label: 'خاک و آب', icon: Droplets },
    { href: '/sentinel', label: 'ماهواره', icon: Satellite },
    { href: '/ai', label: 'هوش مصنوعی', icon: Brain },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/95 backdrop-blur-xl border-b border-slate-800">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="p-2 bg-emerald-600/20 rounded-lg">
              <Leaf className="w-6 h-6 text-emerald-400" />
            </div>
            <span className="text-xl font-bold text-white">Econojin</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-1">
            {mainLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50 rounded-lg transition-colors"
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>

          <LanguageSwitcher />
          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 text-slate-300 hover:text-white"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="lg:hidden py-4 border-t border-slate-800">
            <div className="flex flex-col gap-1">
              {mainLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50 rounded-lg transition-colors"
                  >
                    <Icon className="w-5 h-5" />
                    <span>{link.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
