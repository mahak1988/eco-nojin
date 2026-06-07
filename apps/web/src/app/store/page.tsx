"use client";

import { useState } from "react";
import Link from "next/link";
import { ShoppingBag, Search, ShoppingCart, Wallet, Star, Plus, CreditCard } from "lucide-react";

const SAMPLE_PRODUCTS = [
  { id: 1, name: "بذر گندم مقاوم به خشکی", price: 450000, discount_price: 380000, stock: 150, image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600", seller: "مؤسسه بذر" },
  { id: 2, name: "سنسور رطوبت خاک TDR", price: 2500000, discount_price: null, stock: 45, image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600", seller: "اکو نوژین" },
  { id: 3, name: "کود هیومیک اسید مایع", price: 850000, discount_price: 720000, stock: 80, image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600", seller: "کود سبز" },
];

export default function StorePage() {
  const [cart, setCart] = useState([]);
  const [walletBalance, setWalletBalance] = useState(5000000);
  const [showWalletModal, setShowWalletModal] = useState(false);
  const [depositAmount, setDepositAmount] = useState("");

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) setCart(cart.map(item => item.id === product.id ? {...item, qty: item.qty + 1} : item));
    else setCart([...cart, {...product, qty: 1}]);
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.discount_price || item.price) * item.qty, 0);

  const handleDeposit = () => {
    if (!depositAmount) return;
    setWalletBalance(prev => prev + parseInt(depositAmount));
    setShowWalletModal(false);
    setDepositAmount("");
    alert("کیف پول با موفقیت شارژ شد!");
  };

  const handleCheckout = () => {
    if (cartTotal > walletBalance) {
      alert("موجودی کافی نیست. لطفاً کیف پول را شارژ کنید.");
      setShowWalletModal(true);
      return;
    }
    setWalletBalance(prev => prev - cartTotal);
    setCart([]);
    alert("سفارش با موفقیت ثبت شد!");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-emerald-400">بازگشت به اکو نوژین</Link>
          <div className="flex-1 max-w-xl mx-8 relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input type="text" placeholder="جستجو در محصولات..." className="w-full pr-10 pl-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none" />
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setShowWalletModal(true)} className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-xl">
              <Wallet className="h-5 w-5 text-emerald-400" />
              <span className="font-bold">{walletBalance.toLocaleString()} تومان</span>
            </button>
            <div className="relative">
              <ShoppingCart className="h-6 w-6 text-slate-300" />
              {cart.length > 0 && <span className="absolute -top-2 -right-2 w-5 h-5 bg-emerald-500 text-white text-xs rounded-full flex items-center justify-center">{cart.reduce((sum, item) => sum + item.qty, 0)}</span>}
            </div>
          </div>
        </div>
      </header>

      <section className="container mx-auto px-6 py-12">
        <h1 className="text-4xl font-black text-white mb-8">فروشگاه تخصصی اکو نوژین</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SAMPLE_PRODUCTS.map((product) => (
            <div key={product.id} className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-emerald-500/50 transition-all">
              <img src={product.image} alt={product.name} className="w-full h-48 object-cover" />
              <div className="p-5">
                <h3 className="text-lg font-bold text-white mb-2">{product.name}</h3>
                <div className="flex items-center gap-2 mb-4 text-sm text-slate-400">
                  <Star className="h-4 w-4 text-amber-400 fill-current" />
                  <span>فروشنده: {product.seller}</span>
                </div>
                <div className="flex items-end justify-between">
                  <div>
                    {product.discount_price && <div className="text-sm text-slate-500 line-through">{product.price.toLocaleString()}</div>}
                    <div className="text-xl font-black text-emerald-400">{(product.discount_price || product.price).toLocaleString()} تومان</div>
                  </div>
                  <button onClick={() => addToCart(product)} className="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl"><Plus className="h-5 w-5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {cart.length > 0 && (
        <div className="fixed bottom-6 right-6 bg-slate-900 border border-emerald-500/30 rounded-2xl p-5 shadow-2xl w-80">
          <h3 className="font-bold text-white mb-3">سبد خرید</h3>
          <div className="text-sm text-slate-300 mb-3">جمع کل: <span className="text-white font-bold">{cartTotal.toLocaleString()} تومان</span></div>
          <button onClick={handleCheckout} className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
            <CreditCard className="h-5 w-5" /> پرداخت و ثبت سفارش
          </button>
        </div>
      )}

      {showWalletModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-white mb-4">شارژ کیف پول</h3>
            <input type="number" value={depositAmount} onChange={(e) => setDepositAmount(e.target.value)} placeholder="مبلغ به تومان" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white mb-4" />
            <div className="flex gap-3">
              <button onClick={() => setShowWalletModal(false)} className="flex-1 py-3 bg-slate-800 text-white rounded-xl">انصراف</button>
              <button onClick={handleDeposit} className="flex-1 py-3 bg-emerald-600 text-white rounded-xl font-bold">پرداخت</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}