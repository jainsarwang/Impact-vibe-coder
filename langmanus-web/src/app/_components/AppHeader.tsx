export function AppHeader() {
  return (
    <header className="relative flex w-full items-center justify-between px-6 pb-8 pt-6">
      {/* Logo Section - Ensure logo.png is in your public folder */}
      <div className="left-4 top-4 z-50 h-16 w-16 overflow-hidden rounded-lg bg-white shadow-lg">
        <img
          src="/logo.png"
          alt="Logo"
          className="h-full w-full object-contain p-1" // object-contain might be better for logos
        />
      </div>
      {/* Title */}
      <div>
        <a
          href="/image-to-code"
          className="inline-flex w-full transform cursor-pointer items-center justify-center rounded-lg bg-blue-600 px-6 py-3 font-bold text-white shadow-md transition-all duration-200 hover:-translate-y-0.5 hover:bg-blue-700 hover:shadow-lg md:w-auto"
        >
          Image to code
        </a>
      </div>
    </header>
  );
}
