import React from 'react';
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/react-router';

export function RequireClerkAuth({ children }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
