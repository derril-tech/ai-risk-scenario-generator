import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { LoginDto } from './dto/login.dto';

@Injectable()
export class AuthService {
    constructor(private jwtService: JwtService) { }

    async login(loginDto: LoginDto) {
        // TODO: Implement proper user validation
        // For now, return a mock token for development
        const payload = { email: loginDto.email, sub: 'mock-user-id' };
        return {
            access_token: this.jwtService.sign(payload),
            user: {
                id: 'mock-user-id',
                email: loginDto.email,
                name: 'Mock User',
            },
        };
    }

    async validateUser(payload: any) {
        // TODO: Implement user validation from database
        return { id: payload.sub, email: payload.email };
    }
}
