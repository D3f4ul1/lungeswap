package com.nat3r.spearswap;

import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;

/**
 * The swap state machine. This is the original SpearSwapper {@code SwapManager}, unchanged.
 *
 * <p>State 1: select the spear, force an attack, move to state 2.
 * State 2: wait {@link #DELAY_TICKS}, then revert.
 *
 * <p>Note it sends <b>no</b> slot packets by hand. Selecting the spear and then calling
 * {@code doAttack()} makes vanilla's own {@code ClientPlayerInteractionManager.attackEntity}
 * emit {@code slot->spear} (via {@code syncSelectedSlot()}) immediately followed by the attack
 * packet, which is exactly the ordering required.
 */
public final class SwapManager {

    /** Ticks the spear stays selected before reverting. */
    private static final int DELAY_TICKS = 1;

    private static final int IDLE = 0;
    private static final int ATTACK = 1;
    private static final int HOLD = 2;

    private static int swapState = IDLE;
    private static int targetSlot = -1;
    private static int originalSlot = -1;
    private static int ticksWaited = 0;

    private SwapManager() {
    }

    public static void startSwap(int target, int original) {
        if (swapState == IDLE) {
            targetSlot = target;
            originalSlot = original;
            swapState = ATTACK;
            ticksWaited = 0;
        }
    }

    public static void tick(MinecraftClient mc) {
        if (mc.player == null) {
            return;
        }

        if (swapState == ATTACK) {
            mc.player.getInventory().setSelectedSlot(targetSlot);

            // Mirrors the original: mark the attack key as pressed so the game also treats this as
            // a real click. Wrapped, because the original wrapped it too.
            try {
                InputUtil.Key key = KeyBindingHelper.getBoundKeyOf(mc.options.attackKey);
                KeyBinding.onKeyPressed(key);
            } catch (Exception ignored) {
                // original behaviour: swallow
            }
            mc.options.attackKey.setPressed(true);

            // MAPPING: doAttack() is private in Yarn; widened via spearswap.accesswidener.
            mc.doAttack();

            swapState = HOLD;
            ticksWaited = 0;
        } else if (swapState == HOLD) {
            ticksWaited++;
            if (ticksWaited >= DELAY_TICKS) {
                mc.options.attackKey.setPressed(false);
                mc.player.getInventory().setSelectedSlot(originalSlot);
                swapState = IDLE;
            }
        }
    }
}
