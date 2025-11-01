import { SignedIn, SignedOut } from "@clerk/nextjs";

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-16 md:py-24">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6 leading-tight">
          Welcome to{" "}
          <span className="text-primary">OpenForge</span>
        </h1>
        <p className="text-lg md:text-xl lg:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
          A unified, real-time, AI-assisted platform that fundamentally redefines open-source collaboration.
        </p>
        <SignedOut>
          <p className="text-base text-muted-foreground mb-4">
            Sign in or sign up to get started with your open-source projects.
          </p>
        </SignedOut>
        <SignedIn>
          <p className="text-base text-muted-foreground mb-4">
            Welcome back! Your dashboard is ready.
          </p>
        </SignedIn>
      </div>
    </main>
  );
}
