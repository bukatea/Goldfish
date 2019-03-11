#include "tb.hpp"
#include "notation.hpp"

#include "gtest/gtest.h"

using namespace goldfish;

TEST(TableBase, init) {
    const bool result = tb::initialize("/Users/bendik/drive/div/Goldfish/syzygy");
    ASSERT_TRUE(result);

    ASSERT_LE(5U, tb::MAX_MAN);
}

TEST(TableBase, probe_wdl) {
    ASSERT_LT(0U, tb::MAX_MAN) << "No tablebase entries!";
    const Position pos_initial(Notation::to_position(Notation::STANDARDPOSITION));            // Initial position
    const Position pos_win_Kc2(Notation::to_position("8/8/8/8/5kp1/P7/8/1K1N4 w - - 0 1"));   // Kc2 - mate
    const Position pos_win_Na2(Notation::to_position("8/8/8/5N2/8/p7/8/2NK3k w - - 0 1"));   // Na2 - mate
    const Position pos_draw(Notation::to_position("8/3k4/8/8/8/4B3/4KB2/2B5 w - - 0 1"));   // Draw

    ASSERT_EQ(tb::Outcome::FAILED_PROBE, tb::probe_outcome(pos_initial));
    ASSERT_EQ(tb::Outcome::WIN, tb::probe_outcome(pos_win_Kc2));
    ASSERT_EQ(tb::Outcome::WIN, tb::probe_outcome(pos_win_Na2));
    ASSERT_EQ(tb::Outcome::DRAW, tb::probe_outcome(pos_draw));
}

TEST(TableBase, probe_root) {
    ASSERT_LT(0U, tb::MAX_MAN) << "No tablebase entries!";
    const Position pos_initial(Notation::to_position(Notation::STANDARDPOSITION));            // Initial position
    const Position pos_win_Kc2(Notation::to_position("8/8/8/8/5kp1/P7/8/1K1N4 w - - 0 1"));   // Kc2 - mate
    const Position pos_checkmate(Notation::to_position("8/8/8/8/6N1/8/3K4/5k1Q b - - 2 10")); // Checkmate
    const Position pos_stalemate(Notation::to_position("8/8/8/8/6N1/8/3K1Q2/7k b - - 6 12")); // Stalemate
    const Position pos_draw(Notation::to_position("8/3k4/8/8/8/4B3/4KB2/2B5 w - - 0 1"));   // Draw

    tb::TableResult tb_initial = tb::probe_root(pos_initial);
    tb::TableResult tb_win_Kc2 = tb::probe_root(pos_win_Kc2);
    tb::TableResult tb_checkmate = tb::probe_root(pos_checkmate);
    tb::TableResult tb_stalemate = tb::probe_root(pos_stalemate);
    tb::TableResult tb_draw = tb::probe_root(pos_draw);

    // Initial position.
    ASSERT_EQ(tb::Outcome::FAILED_PROBE, tb_initial.outcome());
    ASSERT_TRUE(tb_initial.failed());
    ASSERT_FALSE(tb_initial.checkmate());
    ASSERT_FALSE(tb_initial.stalemate());

    // Known win.
    ASSERT_EQ(tb::Outcome::WIN, tb_win_Kc2.outcome());
    ASSERT_FALSE(tb_win_Kc2.failed());
    ASSERT_FALSE(tb_win_Kc2.checkmate());
    ASSERT_FALSE(tb_win_Kc2.stalemate());
    ASSERT_EQ(5U, tb_win_Kc2.distance_to_zero());
    ASSERT_EQ(Square::B1, tb_win_Kc2.from_square());
    ASSERT_EQ(Square::C2, tb_win_Kc2.to_square());

    // Checkmate.
    ASSERT_EQ(tb::Outcome::WIN, tb_checkmate.outcome());
    ASSERT_FALSE(tb_checkmate.failed());
    ASSERT_TRUE(tb_checkmate.checkmate());
    ASSERT_FALSE(tb_checkmate.stalemate());
    ASSERT_EQ(0U, tb_checkmate.distance_to_zero());

    // Stalemate.
    ASSERT_EQ(tb::Outcome::DRAW, tb_stalemate.outcome());
    ASSERT_FALSE(tb_stalemate.failed());
    ASSERT_FALSE(tb_stalemate.checkmate());
    ASSERT_TRUE(tb_stalemate.stalemate());
    ASSERT_EQ(0U, tb_stalemate.distance_to_zero());

    // Known draw.
    ASSERT_EQ(tb::Outcome::DRAW, tb_draw.outcome());
    ASSERT_FALSE(tb_draw.failed());
    ASSERT_FALSE(tb_draw.checkmate());
    ASSERT_FALSE(tb_draw.stalemate());
    ASSERT_EQ(0U, tb_draw.distance_to_zero());
}
