import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { firstName, lastName, email, password, acceptTerms } = body

    // 1. Validation checks
    if (!acceptTerms) {
      return NextResponse.json(
        { error: 'You must accept the Terms of Service and Privacy Policy to register.' },
        { status: 400 }
      )
    }

    if (!firstName || !lastName || !email || !password) {
      return NextResponse.json(
        { error: 'All fields are required.' },
        { status: 400 }
      )
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters long.' },
        { status: 400 }
      )
    }

    // 2. Insert user into database / auth provider here (e.g. Prisma / Neon DB / NextAuth)
    // Example: await db.user.create({ data: { firstName, lastName, email, hashedPassword } })

    return NextResponse.json(
      { message: 'Account created successfully!', user: { firstName, email } },
      { status: 201 }
    )
  } catch (error) {
    return NextResponse.json(
      { error: 'An unexpected error occurred during registration.' },
      { status: 500 }
    )
  }
}
