import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";
import { Outlet, Link, Navigate } from "react-router-dom";

export function Layout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-content">
          <h1>Coding Challenge Generator</h1>

          <nav>
            <SignedIn>
              <Link to="/"> Generate Challenge </Link>
              <Link to="/history"> History </Link>
              <UserButton />
            </SignedIn>

            <SignedOut>
              <Navigate to="/sign-in" />
            </SignedOut>
          </nav>
        </div>
      </header>

      <main className="app-main">
        <SignedOut>
          <Navigate to="./sign-in" replace />
        </SignedOut>
        <SignedIn>
          <Outlet />
        </SignedIn>
      </main>
    </div>
  );
}
