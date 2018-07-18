#pragma once

namespace goldfish {

enum MoveType {
    NORMAL, PAWN_DOUBLE, PAWN_PROMOTION,
    EN_PASSANT, CASTLING, NO_MOVE_TYPE,
};

namespace MoveTypes {
constexpr int MASK = 0x7;
}

}
