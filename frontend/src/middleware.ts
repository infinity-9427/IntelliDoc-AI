import type { MiddlewareConfig } from "next/server";
import createMiddleware from "next-intl/middleware";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { locales } from "@/i18n/routing"

const handleI18nRouting = createMiddleware( {
  locales,
  defaultLocale: "en",
} );

export default async function middleware( request: NextRequest ) {
  const response = handleI18nRouting( request );
  // const protectedRoutes = ["/dashboard"];
  // const isAuthenticated = request.cookies.get( "isAuthenticated" )?.value === "true";
  // const currentPath = request.nextUrl.pathname;

  // if ( !isAuthenticated && protectedRoutes.some( ( route ) => currentPath.startsWith( route ) ) ) {
  //   const absoluteURL = new URL( "/login", request.nextUrl.origin );
  //   return NextResponse.redirect( absoluteURL );
  // }

  return response;
}

export const config: MiddlewareConfig = {
  matcher: [
    "/((?!api|_next|static|favicon.ico|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(es|en|fr|it|pr|de)/:path*",
    ],
  };

