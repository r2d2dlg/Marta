import NextAuth, { Account, Profile, Session, User } from "next-auth"; // Import necessary types
import { JWT } from "next-auth/jwt"; // Import JWT type
import GoogleProvider from "next-auth/providers/google";

// Define a custom type for your session to include accessToken
interface CustomSession extends Session {
  accessToken?: string;
}

// Define a custom type for your JWT token to include accessToken and other properties
interface CustomJWT extends JWT {
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: number;
  idToken?: string;
}

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
      authorization: {
        params: {
          scope: 'email profile openid https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send',
          prompt: 'consent', // Add this to force consent screen
          access_type: 'offline', // Add this to ensure refresh token
        },
      },
    }),
  ],
  callbacks: {
    // Add types to the jwt callback parameters
    async jwt({ token, account, profile }: { token: CustomJWT; account?: Account | null; profile?: Profile; user?: User }) {
      // Persist the OAuth access_token and other data to the JWT right after sign-in
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token; // Google might not always provide a refresh token
        token.expiresAt = account.expires_at; // Access token expiry time (in seconds)
        token.idToken = account.id_token; // OpenID Connect ID Token
      }

      // Optional: Implement token refresh logic here if you need long-term access
      // Check if the access token has expired. expiresAt is in seconds.
      // if (token.expiresAt && (token.expiresAt as number) * 1000 < Date.now()) {
      //   // Token is expired, attempt to refresh
      //   // You would call a function here to exchange the refresh token for a new access token
      //   // token = await refreshAccessToken(token); // You would implement refreshAccessToken
      // }
      return token;
    },
    // Add types to the session callback parameters
    async session({ session, token }) {
      // Send properties to the client, such as an access_token from a provider.
      session.accessToken = token.accessToken as string | undefined;
      // If there was an error refreshing the token, expose it to the client
      if (token.error) {
        session.error = token.error as string;
      }
      return session;
    }
  },
  secret: process.env.NEXTAUTH_SECRET,
  // debug: process.env.NODE_ENV === 'development',
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
