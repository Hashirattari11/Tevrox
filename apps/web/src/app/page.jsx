export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-50 to-emerald-100 font-sans relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-100 rounded-full blur-3xl opacity-40" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-slate-200 rounded-full blur-3xl opacity-40" />

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <div className="flex items-center justify-between mb-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold text-lg">T</div>
            <span className="text-xl font-bold text-slate-900 font-serif tracking-tight">Tevrox</span>
          </div>
          <div className="flex items-center gap-8 px-8">
            <a href="/products" className="text-sm font-medium text-slate-600 hover:text-emerald-600 transition-colors">Products</a>
            <a href="/dashboard" className="text-sm font-medium text-slate-600 hover:text-emerald-600 transition-colors">Dashboard</a>
            <a href="/admin/products" className="text-sm font-medium text-slate-600 hover:text-emerald-600 transition-colors">Admin</a>
          </div>
          <div className="flex items-center gap-4">
            <a href="/login" className="text-sm font-medium text-slate-600 hover:text-emerald-600 transition-colors">Log in</a>
            <button className="px-4 py-2 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-700 transition-all">Sign up</button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold uppercase tracking-wider animate-bounce">
              <span className="relative -top-px h-2 w-2 rounded-full bg-emerald-600 animate-ping" />
              Tevrox · Phase 3 Live
            </div>
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-slate-900 leading-[1.1] mb-6">
              Skincare &amp; Nutrition,<br />
              <span className="text-emerald-600">Connected.</span>
            </h1>
            <p className="text-lg text-slate-600 max-w-lg leading-relaxed">
              Discover, scan, and track your skincare products. Find ingredients that work for you and get admin-verified recommendations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <a href="/dashboard" className="px-8 py-4 rounded-xl bg-emerald-600 text-white font-semibold text-lg hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition-all shadow-lg">
                Get Started <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </a>
              <a href="/products" className="px-8 py-4 rounded-xl border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition-all">Browse Products</a>
            </div>
          </div>
          <div className="flex flex-col gap-4">
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600 text-xs font-bold">✅</div>
                  <div>
                    <div className="text-sm font-semibold text-slate-900">Cleanser Verified</div>
                    <div className="text-xs text-slate-500">Vanilla Cleanser • Barcode: 123456</div>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-green-600 shadow-md">✅</div>
                </div>
              </div>
              <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 p-4 mt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600"><span class="w-5 h-5">✨</span></div>
                    <div>
                      <div className="text-sm font-semibold text-slate-900">Serum Analyzed</div>
                      <div className="text-xs text-slate-500">Vitamin C Serum • Unverified</div>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center text-yellow-600 shadow-md"><span class="w-5 h-5">🔥</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Why Choose Tevrox?</h2>
            <p className="text-lg text-slate-600 mt-4">Everything you need for skincare intelligence</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[{
              title: "Product Search",
              desc: "Find products by name, brand, or ingredient."
            },
            { title: "Barcode Scanner", desc: "Scan barcodes for instant product lookup." },
            { title: "Admin Verified", desc: "All products are admin-verified for safety." },
          ].map((feature) => (
            <div key={feature.title} className="p-6 rounded-xl border border-slate-200 bg-white hover:shadow-md transition-all hover:border-emerald-200 hover:bg-emerald-50">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-4 text-emerald-600 text-xl">✨</div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-500">{feature.desc}</p>
            </div>
          ))}
        </div>
        </div>

        <div className="max-w-2xl mx-auto text-center py-12">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Ready to get started?</h2>
          <p className="text-lg text-slate-600 mb-8">Join thousands of users tracking their skincare products.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/dashboard" className="px-8 py-4 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition-all">
                Go to Dashboard <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </a>
            <a href="/products" className="px-8 py-4 rounded-xl border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition-all">Browse Products</a>
          </div>
        </div>

        <footer className="border-t border-slate-200 bg-slate-50 py-8 px-6">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-emerald-600 flex items-center justify-center text-white text-sm font-bold">T</div>
              <span className="font-bold text-slate-900">Tevrox</span>
            </div>
            <div className="text-sm text-slate-600">© {new Date().getFullYear()} Tevrox Inc. All rights reserved.</div>
            <div className="flex gap-4">
              <a href="/" className="text-sm text-slate-600 hover:text-emerald-600">Terms</Link>
              <a href="/" className="text-sm text-slate-600 hover:text-emerald-600">Privacy</Link>
              <a href="/login" className="text-sm font-medium text-emerald-600 hover:text-emerald-700">Log in</a>
              <a href="/signup" className="px-3 py-2 rounded-md bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700">Sign up</a>
            </div>
          </div>
        </footer>
      </div>
    </main>
  );
}
